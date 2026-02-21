"""
Service: Admin Service
Provides all admin-level data queries — users, documents, AI usage, system stats.
Only callable by users with is_admin=1.
"""
from sqlalchemy import text
from database.connection import get_db
from datetime import datetime, timedelta


# ── Guard ─────────────────────────────────────────────────────
def require_admin(user: dict):
    if not user or not user.get("is_admin"):
        raise PermissionError("Admin access required.")


# ── User Management ───────────────────────────────────────────
def get_all_users(search: str = "", plan_filter: str = "all") -> list[dict]:
    with get_db() as db:
        query = """
            SELECT id, email, full_name, plan, is_active, is_admin,
                   docs_used_this_month, docs_limit,
                   last_login_at, created_at
            FROM users
            WHERE (:search = '' OR email LIKE :like OR full_name LIKE :like)
              AND (:plan   = 'all' OR plan = :plan)
            ORDER BY created_at DESC
        """
        rows = db.execute(text(query), {
            "search": search, "like": f"%{search}%", "plan": plan_filter
        }).fetchall()
        return [dict(r._mapping) for r in rows]


def set_user_plan(user_id: str, new_plan: str) -> bool:
    limits = {"free": 3, "pro": 999999, "enterprise": 999999}
    with get_db() as db:
        db.execute(text("""
            UPDATE users SET plan=:plan, docs_limit=:lim,
                             updated_at=CURRENT_TIMESTAMP
            WHERE id=:uid
        """), {"plan": new_plan, "lim": limits.get(new_plan, 3), "uid": user_id})
        db.commit()
    return True


def toggle_user_active(user_id: str, active: bool) -> bool:
    with get_db() as db:
        db.execute(text(
            "UPDATE users SET is_active=:a, updated_at=CURRENT_TIMESTAMP WHERE id=:uid"
        ), {"a": int(active), "uid": user_id})
        db.commit()
    return True


def toggle_user_admin(user_id: str, is_admin: bool) -> bool:
    with get_db() as db:
        db.execute(text(
            "UPDATE users SET is_admin=:a, updated_at=CURRENT_TIMESTAMP WHERE id=:uid"
        ), {"a": int(is_admin), "uid": user_id})
        db.commit()
    return True


def delete_user(user_id: str) -> bool:
    with get_db() as db:
        db.execute(text("DELETE FROM users WHERE id=:uid"), {"uid": user_id})
        db.commit()
    return True


# ── Document Overview ─────────────────────────────────────────
def get_all_documents(limit: int = 100, user_filter: str = "") -> list[dict]:
    with get_db() as db:
        query = """
            SELECT d.id, d.title, d.domain, d.status, d.input_type,
                   d.completeness_score, d.generation_time_ms, d.created_at,
                   u.email, u.full_name
            FROM documents d
            JOIN users u ON d.user_id = u.id
            WHERE (:uf = '' OR u.email LIKE :like OR u.full_name LIKE :like)
            ORDER BY d.created_at DESC
            LIMIT :lim
        """
        rows = db.execute(text(query), {
            "uf": user_filter, "like": f"%{user_filter}%", "lim": limit
        }).fetchall()
        return [dict(r._mapping) for r in rows]


# ── AI Usage Stats ────────────────────────────────────────────
def get_ai_usage_stats(days: int = 30) -> list[dict]:
    with get_db() as db:
        since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        rows = db.execute(text("""
            SELECT chain_name,
                   COUNT(*) AS total_calls,
                   SUM(total_tokens) AS total_tokens,
                   SUM(estimated_cost_usd) AS total_cost,
                   AVG(latency_ms) AS avg_latency_ms,
                   SUM(CASE WHEN status='error' THEN 1 ELSE 0 END) AS errors
            FROM ai_usage_logs
            WHERE created_at >= :since
            GROUP BY chain_name
            ORDER BY total_calls DESC
        """), {"since": since}).fetchall()
        return [dict(r._mapping) for r in rows]


def get_ai_usage_by_model(days: int = 30) -> list[dict]:
    with get_db() as db:
        since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        rows = db.execute(text("""
            SELECT model,
                   COUNT(*) AS total_calls,
                   SUM(total_tokens) AS total_tokens,
                   SUM(estimated_cost_usd) AS total_cost
            FROM ai_usage_logs
            WHERE created_at >= :since
            GROUP BY model
            ORDER BY total_calls DESC
        """), {"since": since}).fetchall()
        return [dict(r._mapping) for r in rows]


def get_usage_by_user(days: int = 30) -> list[dict]:
    with get_db() as db:
        since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        rows = db.execute(text("""
            SELECT u.email, u.plan,
                   COUNT(l.id) AS api_calls,
                   SUM(l.total_tokens) AS tokens,
                   SUM(l.estimated_cost_usd) AS cost_usd
            FROM ai_usage_logs l
            JOIN users u ON l.user_id = u.id
            WHERE l.created_at >= :since
            GROUP BY u.id, u.email, u.plan
            ORDER BY tokens DESC
        """), {"since": since}).fetchall()
        return [dict(r._mapping) for r in rows]


# ── System Dashboard Stats ────────────────────────────────────
def get_system_stats() -> dict:
    with get_db() as db:
        def scalar(sql, params=None):
            return db.execute(text(sql), params or {}).scalar() or 0

        return {
            "total_users":    scalar("SELECT COUNT(*) FROM users"),
            "active_users":   scalar("SELECT COUNT(*) FROM users WHERE is_active=1"),
            "pro_users":      scalar("SELECT COUNT(*) FROM users WHERE plan='pro'"),
            "free_users":     scalar("SELECT COUNT(*) FROM users WHERE plan='free'"),
            "total_docs":     scalar("SELECT COUNT(*) FROM documents"),
            "completed_docs": scalar("SELECT COUNT(*) FROM documents WHERE status='completed'"),
            "failed_docs":    scalar("SELECT COUNT(*) FROM documents WHERE status='failed'"),
            "docs_today":     scalar(
                "SELECT COUNT(*) FROM documents WHERE DATE(created_at)=CURDATE()"),
            "docs_this_week": scalar(
                "SELECT COUNT(*) FROM documents WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"),
            "total_tokens":   scalar("SELECT SUM(total_tokens) FROM ai_usage_logs"),
            "total_cost":     scalar("SELECT SUM(estimated_cost_usd) FROM ai_usage_logs"),
            "new_users_today":scalar(
                "SELECT COUNT(*) FROM users WHERE DATE(created_at)=CURDATE()"),
        }
