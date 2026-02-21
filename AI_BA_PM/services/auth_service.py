"""
Service: Auth Service
User registration, login, session management for Streamlit.
Uses bcrypt directly for password hashing (passlib incompatible with Python 3.14).
"""
import uuid
import bcrypt
from typing import Optional
from sqlalchemy import text
from database.connection import get_db


# ── Password Utilities ────────────────────────────────────────
def hash_password(password: str) -> str:
    """
    Hash password with bcrypt.
    Truncates to 72 bytes — bcrypt's hard limit.
    """
    pw_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        pw_bytes = plain.encode("utf-8")[:72]
        return bcrypt.checkpw(pw_bytes, hashed.encode("utf-8"))
    except Exception:
        return False


# ── User Operations ───────────────────────────────────────────
def register_user(email: str, password: str, full_name: str) -> tuple[bool, str]:
    """
    Create a new user. Returns (success, message).
    """
    email = email.strip().lower()
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not email or "@" not in email:
        return False, "Invalid email address."

    with get_db() as db:
        existing = db.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": email}
        ).fetchone()

        if existing:
            return False, "An account with this email already exists."

        user_id = str(uuid.uuid4())
        pwd_hash = hash_password(password)
        db.execute(
            text("""
                INSERT INTO users (id, email, password_hash, full_name, plan, docs_limit)
                VALUES (:id, :email, :pw, :name, 'free', 3)
            """),
            {"id": user_id, "email": email, "pw": pwd_hash, "name": full_name.strip()}
        )
    return True, "Account created successfully!"


def login_user(email: str, password: str) -> tuple[bool, Optional[dict], str]:
    """
    Authenticate a user. Returns (success, user_dict | None, message).
    """
    email = email.strip().lower()
    with get_db() as db:
        row = db.execute(
            text("SELECT id, email, password_hash, full_name, plan, docs_used_this_month, docs_limit, is_admin FROM users WHERE email = :email AND is_active = 1"),
            {"email": email}
        ).fetchone()

        if not row:
            return False, None, "Invalid email or password."

        if not verify_password(password, row.password_hash):
            return False, None, "Invalid email or password."

        # Update last_login
        db.execute(
            text("UPDATE users SET last_login_at = NOW() WHERE id = :id"),
            {"id": row.id}
        )

        user = {
            "id":        row.id,
            "email":     row.email,
            "full_name": row.full_name,
            "plan":      row.plan,
            "docs_used": row.docs_used_this_month,
            "docs_limit":row.docs_limit,
            "is_admin":  bool(row.is_admin),
        }
        return True, user, "Login successful!"


def get_user_by_id(user_id: str) -> Optional[dict]:
    with get_db() as db:
        row = db.execute(
            text("SELECT id, email, full_name, plan, docs_used_this_month, docs_limit, is_admin FROM users WHERE id = :id"),
            {"id": user_id}
        ).fetchone()
        if not row:
            return None
        return {
            "id": row.id, "email": row.email, "full_name": row.full_name,
            "plan": row.plan, "docs_used": row.docs_used_this_month,
            "docs_limit": row.docs_limit, "is_admin": bool(row.is_admin)
        }


def can_generate(user: dict) -> tuple[bool, str]:
    """Check if the user has remaining quota."""
    if user["docs_used"] >= user["docs_limit"]:
        return False, f"You've used {user['docs_used']}/{user['docs_limit']} documents this month. Upgrade to Pro for unlimited."
    return True, ""


def increment_doc_count(user_id: str) -> None:
    with get_db() as db:
        db.execute(
            text("UPDATE users SET docs_used_this_month = docs_used_this_month + 1 WHERE id = :id"),
            {"id": user_id}
        )
