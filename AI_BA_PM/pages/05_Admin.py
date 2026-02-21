"""
Page: Admin Panel
Full admin dashboard — visible only to users with is_admin=1.
Sections: Dashboard, Users, Documents, AI Usage, System Tools
"""
import time
import streamlit as st

st.set_page_config(page_title="Admin Panel — RequirementIQ", page_icon="🛡️", layout="wide")

# Lazy import — keeps page registering even if DB is slow
try:
    from services.admin_service import (
        get_system_stats, get_all_users, get_all_documents,
        get_ai_usage_stats, get_usage_by_user, get_ai_usage_by_model,
        set_user_plan, toggle_user_active, toggle_user_admin, delete_user
    )
    _admin_svc_ok = True
except Exception as _e:
    _admin_svc_ok = False
    _admin_svc_err = str(_e)

# ── Auth + Admin Guard ────────────────────────────────────────
if not st.session_state.get("user"):
    st.error("🔒 Please log in first.")
    st.stop()

user = st.session_state.user
if not user.get("is_admin"):
    st.error("⛔ Access Denied — Admin privileges required.")
    st.stop()

# ── Page CSS ──────────────────────────────────────────────────
from utils.ui_theme import inject_theme
inject_theme()

st.markdown("""
<div class="admin-header" style="padding: 1.5rem; margin-bottom: 2rem;">
  <h1 style="font-size: 2.2rem; margin-bottom: 0.5rem; color: #f8fafc;">🛡️ Admin Control Panel</h1>
  <p style="color: #a5b4fc; font-size: 1rem; margin: 0;">Full system access — RequirementIQ</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────
tab_dash, tab_users, tab_docs, tab_ai, tab_tools = st.tabs([
    "📊 Dashboard", "👥 Users", "📄 Documents", "🤖 AI Usage", "⚙️ Tools"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — Dashboard
# ══════════════════════════════════════════════════════════════
with tab_dash:
    try:
        s = get_system_stats()
        
        with st.container(border=True):
            st.markdown("<h4 style='color: white; margin-bottom: 1rem;'>👥 Platform Users</h4>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Users",    s["total_users"])
            c2.metric("Active Users",   s["active_users"])
            c3.metric("Pro Users",      s["pro_users"])
            c4.metric("New Today",      s["new_users_today"])
            
        with st.container(border=True):
            st.markdown("<h4 style='color: white; margin-bottom: 1rem;'>📄 Generated Documents</h4>", unsafe_allow_html=True)
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Total Docs",      s["total_docs"])
            d2.metric("✅ Completed",    s["completed_docs"])
            d3.metric("❌ Failed",       s["failed_docs"])
            d4.metric("📅 Today",        s["docs_today"])

        with st.container(border=True):
            st.markdown("<h4 style='color: white; margin-bottom: 1rem;'>🤖 Global AI Usage</h4>", unsafe_allow_html=True)
            a1, a2 = st.columns(2)
            a1.metric("Total Tokens Used", f"{int(s['total_tokens'] or 0):,}")
            a2.metric("Estimated Cost",    f"${float(s['total_cost'] or 0):.4f}")

    except Exception as e:
        st.error(f"Could not load stats: {e}")

# ══════════════════════════════════════════════════════════════
# TAB 2 — Users
# ══════════════════════════════════════════════════════════════
with tab_users:
    with st.container(border=True):
        st.markdown("<h4 style='color: white; margin-bottom: 1rem;'>👥 All Users</h4>", unsafe_allow_html=True)

        col_s, col_f = st.columns([3, 1])
        with col_s:
            search = st.text_input("🔍 Search by email or name", placeholder="Search users...", label_visibility="collapsed")
        with col_f:
            plan_filter = st.selectbox("Plan", ["all", "free", "pro", "enterprise"], label_visibility="collapsed")

    try:
        users = get_all_users(search=search, plan_filter=plan_filter)
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.caption(f"Showing {len(users)} user(s)")

        for u in users:
            uid   = u["id"]
            email = u["email"]
            name  = u["full_name"] or "—"
            plan  = u["plan"]
            active = bool(u["is_active"])
            is_adm = bool(u["is_admin"])
            docs_used = u["docs_used_this_month"]
            docs_lim  = u["docs_limit"]
            joined = str(u["created_at"])[:10]
            last_login = str(u["last_login_at"] or "Never")[:16]

            plan_label = "👑 ADMIN" if is_adm else plan.upper()

            with st.expander(f"{'🟢' if active else '🔴'} {email} — {name} [{plan_label}]", expanded=False):
                ic1, ic2, ic3, ic4 = st.columns(4)
                ic1.markdown(f"**Plan:** {plan.upper()}")
                ic2.markdown(f"**Docs:** {docs_used}/{docs_lim}")
                ic3.markdown(f"**Joined:** {joined}")
                ic4.markdown(f"**Last Login:** {last_login}")

                st.markdown("---")
                ac1, ac2, ac3, ac4, ac5 = st.columns(5)

                # Change plan
                with ac1:
                    new_plan = st.selectbox("Change Plan", ["free", "pro", "enterprise"],
                                            index=["free","pro","enterprise"].index(plan),
                                            key=f"plan_{uid}")
                    if new_plan != plan:
                        if st.button("✅ Apply", key=f"apply_plan_{uid}"):
                            set_user_plan(uid, new_plan)
                            st.success("Plan updated!")
                            st.rerun()

                # Toggle active
                with ac2:
                    lbl = "🔴 Deactivate" if active else "🟢 Activate"
                    if st.button(lbl, key=f"active_{uid}"):
                        toggle_user_active(uid, not active)
                        st.rerun()

                # Toggle admin
                with ac3:
                    adm_lbl = "Remove Admin" if is_adm else "👑 Make Admin"
                    if st.button(adm_lbl, key=f"adm_{uid}"):
                        if uid == user["id"]:
                            st.warning("Cannot change your own admin status.")
                        else:
                            toggle_user_admin(uid, not is_adm)
                            st.rerun()

                # Delete user
                with ac4:
                    if st.button("🗑️ Delete", key=f"del_{uid}", type="secondary"):
                        st.session_state[f"confirm_del_{uid}"] = True

                if st.session_state.get(f"confirm_del_{uid}"):
                    with ac5:
                        st.warning("Confirm delete?")
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        if st.button("⚠️ Yes, Delete", key=f"yes_del_{uid}", type="primary"):
                            if uid == user["id"]:
                                st.error("Cannot delete yourself!")
                            else:
                                delete_user(uid)
                                del st.session_state[f"confirm_del_{uid}"]
                                st.success("User deleted.")
                                st.rerun()
                    with cc2:
                        if st.button("Cancel", key=f"no_del_{uid}"):
                            del st.session_state[f"confirm_del_{uid}"]

    except Exception as e:
        st.error(f"Error loading users: {e}")

# ══════════════════════════════════════════════════════════════
# TAB 3 — Documents
# ══════════════════════════════════════════════════════════════
with tab_docs:
    st.markdown("#### 📄 All Documents")

    col_ds, col_dl = st.columns([3, 1])
    with col_ds:
        doc_search = st.text_input("🔍 Filter by user email/name", label_visibility="collapsed",
                                   placeholder="Filter by email or name...")
    with col_dl:
        doc_limit = st.selectbox("Show", [50, 100, 200, 500], label_visibility="collapsed")

    try:
        docs = get_all_documents(limit=doc_limit, user_filter=doc_search)
        st.caption(f"Showing {len(docs)} document(s)")

        if docs:
            status_icon = {"completed":"✅","failed":"❌","processing":"⏳","pending":"⏳","partial":"⚠️"}
            table_data = []
            for d in docs:
                table_data.append({
                    "Status":     status_icon.get(d["status"], "❓"),
                    "Title":      (d["title"] or "Untitled")[:60],
                    "Domain":     d["domain"].upper(),
                    "User":       d["email"],
                    "Input":      d["input_type"],
                    "Score":      f"{d['completeness_score'] or 0}%",
                    "Time (ms)":  d["generation_time_ms"] or 0,
                    "Created":    str(d["created_at"])[:16],
                })
            st.table(table_data)
        else:
            st.info("No documents found.")
    except Exception as e:
        st.error(f"Error loading documents: {e}")

# ══════════════════════════════════════════════════════════════
# TAB 4 — AI Usage
# ══════════════════════════════════════════════════════════════
with tab_ai:
    st.markdown("#### 🤖 AI Chain Usage")

    days = st.slider("Time period (days)", 1, 90, 30)

    col_l, col_m, col_r = st.columns(3)

    with col_l:
        st.markdown("**By Chain**")
        try:
            chain_stats = get_ai_usage_stats(days=days)
            if chain_stats:
                table_data = []
                for r in chain_stats:
                    table_data.append({
                        "Chain":       r["chain_name"].upper(),
                        "Calls":       int(r["total_calls"]),
                        "Tokens":      f"{int(r['total_tokens'] or 0):,}",
                        "Cost":        f"${float(r['total_cost'] or 0):.4f}",
                        "Avg Latency": f"{int(r['avg_latency_ms'] or 0)}ms",
                        "Errors":      int(r["errors"]),
                    })
                st.dataframe(table_data, use_container_width=True, hide_index=True)
            else:
                st.info("No usage data yet.")
        except Exception as e:
            st.error(f"Error: {e}")

    with col_m:
        st.markdown("**By AI Provider (Model)**")
        try:
            model_stats = get_ai_usage_by_model(days=days)
            if model_stats:
                table_data = []
                for r in model_stats:
                    table_data.append({
                        "Model":       str(r["model"]),
                        "Calls":       int(r["total_calls"]),
                        "Tokens":      f"{int(r['total_tokens'] or 0):,}",
                        "Cost":        f"${float(r['total_cost'] or 0):.4f}",
                    })
                st.dataframe(table_data, use_container_width=True, hide_index=True)
            else:
                st.info("No model data yet.")
        except Exception as e:
            st.error(f"Error: {e}")

    with col_r:
        st.markdown("**By User (All)**")
        try:
            user_stats = get_usage_by_user(days=days)
            if user_stats:
                table_data = []
                for r in user_stats:
                    table_data.append({
                        "User":       r["email"],
                        "Plan":       r["plan"].upper(),
                        "Calls":      int(r["api_calls"]),
                        "Tokens":     f"{int(r['tokens'] or 0):,}",
                        "Cost":       f"${float(r['cost_usd'] or 0):.4f}",
                    })
                st.dataframe(table_data, use_container_width=True, hide_index=True)
            else:
                st.info("No user data yet.")
        except Exception as e:
            st.error(f"Error: {e}")

# ══════════════════════════════════════════════════════════════
# TAB 5 — Tools
# ══════════════════════════════════════════════════════════════
with tab_tools:
    st.markdown("#### ⚙️ System Tools")

    st.markdown("**🧠 Active AI Provider**")
    import os
    from config import settings
    current_provider = settings.ai_provider.lower()
    
    new_provider = st.radio("Select AI Provider (applies instantly to all users)",
                            options=["groq", "mistral", "openai"],
                            index=["groq", "mistral", "openai"].index(current_provider),
                            format_func=lambda x: {"groq": "🟢 Groq (Free)", "mistral": "🔵 Mistral", "openai": "🟣 OpenAI"}[x],
                            horizontal=True)
    if new_provider != current_provider:
        if st.button(f"Switch to {new_provider.capitalize()}", type="primary"):
            try:
                # Update .env file
                env_path = ".env"
                if os.path.exists(env_path):
                    with open(env_path, "r") as f:
                        lines = f.readlines()
                    with open(env_path, "w") as f:
                        for line in lines:
                            if line.startswith("AI_PROVIDER="):
                                f.write(f"AI_PROVIDER={new_provider}\n")
                            else:
                                f.write(line)
                st.success(f"✅ Switched to {new_provider.capitalize()}! Restarting app to apply...")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Failed to update .env: {e}")

    st.divider()

    st.markdown("**🔑 Promote User to Admin**")
    promo_email = st.text_input("User email to promote:", placeholder="user@example.com")
    if st.button("👑 Make Admin", type="primary"):
        if promo_email:
            try:
                from sqlalchemy import text
                from database.connection import get_db
                with get_db() as db:
                    result = db.execute(
                        text("UPDATE users SET is_admin=1 WHERE email=:email"),
                        {"email": promo_email}
                    )
                    db.commit()
                    if result.rowcount:
                        st.success(f"✅ {promo_email} is now an admin!")
                    else:
                        st.error("User not found.")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    st.markdown("**🔄 Reset Monthly Doc Counts**")
    st.caption("Resets `docs_used_this_month` to 0 for all users (useful for manual monthly reset).")
    if st.button("Reset All Monthly Counts", type="secondary"):
        try:
            from sqlalchemy import text
            from database.connection import get_db
            with get_db() as db:
                db.execute(text("UPDATE users SET docs_used_this_month=0"))
                db.commit()
            st.success("✅ All monthly document counts reset to 0.")
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()

    st.markdown("**📋 Raw DB Stats**")
    if st.button("Show Table Row Counts"):
        try:
            from sqlalchemy import text
            from database.connection import get_db
            tables = ["users","projects","documents","generated_artifacts",
                      "gap_reports","risk_reports","ai_usage_logs","industry_templates"]
            with get_db() as db:
                stats = {}
                for t in tables:
                    stats[t] = db.execute(text(f"SELECT COUNT(*) FROM `{t}`")).scalar()
            st.table([{"Table": k, "Rows": v} for k, v in stats.items()])
        except Exception as e:
            st.error(f"Error: {e}")
