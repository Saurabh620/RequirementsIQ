"""
Page: Settings
Account info, plan details, AI usage stats, and configuration.
"""
import streamlit as st
from sqlalchemy import text
from database.connection import get_db
from services.auth_service import get_user_by_id

st.set_page_config(page_title="Settings — RequirementIQ", page_icon="⚙️", layout="wide")

if not st.session_state.get("user"):
    st.warning("Please log in.")
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

from utils.ui_theme import inject_theme
inject_theme()

st.markdown("""
<div class="admin-header" style="padding: 1.5rem; margin-bottom: 2rem;">
  <h1 style="font-size: 2.2rem; margin-bottom: 0.5rem; color: #f8fafc;">⚙️ Settings</h1>
  <p style="color: #a5b4fc; font-size: 1rem; margin: 0;">Manage your account, plan upgrades, and API usage tracking.</p>
</div>
""", unsafe_allow_html=True)

tab_account, tab_plan, tab_usage = st.tabs(["👤 Account", "💳 Plan & Billing", "📊 AI Usage"])

with tab_account:
    with st.container(border=True):
        st.markdown("<h4 style='color: white; margin-bottom: 1rem;'>My Information</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Email", value=user["email"], disabled=True)
            st.text_input("Full Name", value=user.get("full_name",""), disabled=True)
            st.text_input("Plan", value=user["plan"].upper(), disabled=True)
        with col2:
            st.markdown(f"""
            <div style="background: rgba(15,23,42,0.6); padding: 1.5rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); height: 100%;">
                <h4 style="margin-top:0; color:#818cf8;">Account Status: ✅ Active</h4>
                <p style="color:#cbd5e1; font-size: 1rem; margin-bottom: 0.5rem;"><b>Documents used:</b> {user['docs_used']} / {user['docs_limit']} this month</p>
                <p style="color:#cbd5e1; font-size: 1rem; margin-bottom: 0;"><b>Remaining:</b> {max(0, user['docs_limit'] - user['docs_used'])} documents</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Log Out", type="secondary"):
        st.session_state.user = None
        for key in ["current_doc", "current_doc_id"]:
            st.session_state.pop(key, None)
        st.switch_page("app.py")

with tab_plan:
    st.markdown("### Current Plan")
    plan = user["plan"]

    col1, col2, col3 = st.columns(3)
    plans = [
        ("🆓 Free", "free", "$0/mo", ["3 documents/month", "BRD + FRD + Agile", "Gap Analysis", "Risk Engine", "PDF + DOCX Export"]),
        ("⚡ Pro", "pro", "$29/mo", ["Unlimited documents", "All Free features", "Priority processing", "Advanced gap detection", "Industry templates"]),
        ("🏢 Enterprise", "enterprise", "$199/mo", ["5 team seats", "All Pro features", "SSO support", "Custom templates", "Priority support"]),
    ]
    for col, (label, plan_key, price, features) in zip([col1, col2, col3], plans):
        with col:
            is_current = plan == plan_key
            border = "2px solid #0075FF" if is_current else "1px solid rgba(255, 255, 255, 0.08)"
            st.markdown(f"""
<div class="vision-card" style="border:{border};text-align:center">
  <h3 style="color:#0075FF;margin:0">{label}</h3>
  <h2 style="color:white;margin:8px 0">{price}</h2>
  {"<div style='background:rgba(0,117,255,0.2);color:#0075FF;border:1px solid #0075FF;border-radius:12px;padding:2px 8px;font-size:0.75rem;margin-bottom:8px;font-weight:bold'>CURRENT PLAN</div>" if is_current else ""}
  {"".join(f"<p style='color:#94a3b8;font-size:0.85rem;margin:4px 0'>✓ {f}</p>" for f in features)}
</div>""", unsafe_allow_html=True)
            if not is_current:
                if st.button(f"Upgrade to {label.split()[1]}", key=f"upgrade_{plan_key}", use_container_width=True, type="primary"):
                    st.info("💳 Stripe integration coming soon. Contact support@requirementiq.com to upgrade.")

with tab_usage:
    with st.container(border=True):
        st.markdown("<h4 style='color: white; margin-bottom: 1rem;'>Usage Overview</h4>", unsafe_allow_html=True)
        try:
            with get_db() as db:
                rows = db.execute(text("""
                    SELECT chain_name, COUNT(*) as calls, SUM(total_tokens) as tokens,
                           SUM(estimated_cost_usd) as cost_usd, AVG(latency_ms) as avg_ms
                    FROM ai_usage_logs
                    WHERE user_id = :uid
                    GROUP BY chain_name
                    ORDER BY tokens DESC
                """), {"uid": user["id"]}).fetchall()

                total_row = db.execute(text("""
                    SELECT COUNT(*) as total_calls, SUM(total_tokens) as total_tokens,
                           SUM(estimated_cost_usd) as total_cost
                    FROM ai_usage_logs WHERE user_id = :uid
                """), {"uid": user["id"]}).fetchone()

            if total_row and total_row.total_calls:
                c1, c2, c3 = st.columns(3)
                c1.metric("Total AI Calls", total_row.total_calls)
                c2.metric("Total Tokens Used", f"{int(total_row.total_tokens or 0):,}")
                c3.metric("Estimated AI Cost", f"${float(total_row.total_cost or 0):.4f}")
                st.divider()

            if rows:
                table_data = [{
                    "Chain": r.chain_name.upper(),
                    "Calls": r.calls,
                    "Tokens": f"{int(r.tokens or 0):,}",
                    "Cost (USD)": f"${float(r.cost_usd or 0):.4f}",
                    "Avg Latency": f"{int(r.avg_ms or 0)}ms"
                } for r in rows]
                st.table(table_data)
            else:
                st.info("No AI usage data yet. Generate your first document!")
        except Exception as e:
            st.error(f"Could not load usage data: {e}")
