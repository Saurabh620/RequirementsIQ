"""
RequirementIQ — Main Streamlit App
Entry point: persistent login / register gate → redirects to dashboard.
Run with: streamlit run app.py

Authentication: JWT tokens stored in browser + database refresh tokens
Auto-login on page load if valid token exists
"""
import streamlit as st
from database.connection import init_db, test_connection
from services.auth_service import login_user, register_user
from services.secure_auth_service import (
    auto_login_from_cookie,
    create_auth_cookie,
    logout_user,
    init_auth_tokens_table,
)
from services.cookie_manager import SimpleAuthCache

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="RequirementIQ — AI Requirements Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────
from utils.ui_theme import inject_theme
inject_theme()


# ── Session State Init ────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "auth_error" not in st.session_state:
    st.session_state.auth_error = ""
if "auth_success" not in st.session_state:
    st.session_state.auth_success = ""
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None


# ── DB Init (once per session) ────────────────────────────────
@st.cache_resource
def startup():
    if not test_connection():
        return False
    init_db()
    # Initialize auth tokens table for persistent login
    init_auth_tokens_table()
    return True


db_ok = startup()


# ── Auto-Login on Page Load ───────────────────────────────────
def auto_login_attempt():
    """
    Attempt to auto-login using cached auth token.
    Called on every page load.
    """
    # Skip if already logged in this session
    if st.session_state.user:
        return
    
    # Check for cached auth token
    cached_token = SimpleAuthCache.get_cached_auth_token()
    if not cached_token:
        return
    
    # Attempt auto-login
    success, user, msg = auto_login_from_cookie(cached_token)
    if success:
        st.session_state.user = user
        st.session_state.auth_token = cached_token
        st.toast("✅ Welcome back!", icon="🔓")
    else:
        # Token invalid/expired, clear it
        SimpleAuthCache.clear_auth_cache()
        st.session_state.auth_token = None


# Perform auto-login on startup
auto_login_attempt()


# ── If already logged in → show dashboard ─────────────────────
if st.session_state.user:
    user = st.session_state.user
    
    # ── Logged-in Sidebar ──
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, {user.get('full_name', '') or 'User'}")
        st.caption(f"📧 {user['email']}")
        st.divider()
        st.markdown("**🚀 Quick Navigation**")
        if st.button("⚡ New Document", use_container_width=True, type="primary"):
            st.switch_page("pages/01_Generate.py")
        if st.button("📁 My Documents", use_container_width=True):
            st.switch_page("pages/03_History.py")
        if st.button("⚙️ Settings", use_container_width=True):
            st.switch_page("pages/04_Settings.py")
        if user.get("is_admin"):
            if st.button("🛡️ Admin Panel", use_container_width=True):
                st.switch_page("pages/05_Admin.py")
        
        st.divider()
        st.markdown("**Account**")
        
        # Logout button with secure token clearing
        if st.button("🚪 Log Out", type="secondary", use_container_width=True):
            # Clear auth token from database
            logout_user(user["id"])
            # Clear from session
            st.session_state.user = None
            st.session_state.auth_token = None
            SimpleAuthCache.clear_auth_cache()
            st.toast("👋 You've been logged out", icon="🔒")
            st.rerun()
        
        st.caption(f"Token expires in ~24 hours. Auto-renewed on login.", font="small")

    # ── Dashboard Main Area ──
    st.markdown("""
    <div class="admin-header" style="padding: 2rem; margin-bottom: 2rem;">
      <h1 style="font-size: 2.5rem; color: #f8fafc; margin-bottom: 0.5rem;">Dashboard Overview</h1>
      <p style="color: #a5b4fc; font-size: 1.1rem; margin: 0;">Monitor your generation metrics and quickly access your artifacts.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color: #f8fafc; margin-top: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem;'>📊 Account Usage</h3>", unsafe_allow_html=True)
    
    # Stats row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stat-box"><h3>{user["docs_used"]}</h3><p>Docs Generated</p></div>', unsafe_allow_html=True)
    with col2:
        remaining = max(0, user["docs_limit"] - user["docs_used"])
        st.markdown(f'<div class="stat-box"><h3>{remaining}</h3><p>Remaining This Month</p></div>', unsafe_allow_html=True)
    with col3:
        plan_label = user["plan"].upper()
        st.markdown(f'<div class="stat-box"><h3>{plan_label}</h3><p>Current Plan</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<h3 style='color: #f8fafc; margin-top: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem;'>⚡ Quick Actions</h3>", unsafe_allow_html=True)
    c_action1, c_action2 = st.columns(2)
    with c_action1:
        st.info("Start a new document generation workflow from uploaded files or voice notes.")
        if st.button("→ Generate New Document", use_container_width=True, type="primary"):
            st.switch_page("pages/01_Generate.py")
    with c_action2:
        st.info("Review, export to PDF/DOCX, and analyze documents you've previously generated.")
        if st.button("→ View Document History", use_container_width=True):
            st.switch_page("pages/03_History.py")

# ── Login / Register ──────────────────────────────────────────
else:
    if not db_ok:
        st.error("⚠️ Cannot connect to the database. Please check your MySQL configuration in `.env`.")
        st.code("DB_HOST=gateway01.ap-southeast-1.prod.aws.tidbcloud.com\\nDB_PORT=4000\\nDB_USERNAME=3gCjNw8RmRfzPzk.root\\nDB_PASSWORD=...\\nDB_DATABASE=test")
        st.stop()

    # Hero / Landing Layout
    col_hero, col_auth = st.columns([1.2, 1], gap="large")
    
    with col_hero:
        st.markdown("""
        <div style="padding: 2rem 0;">
          <h1 style="font-size: 3.5rem; font-weight: 800; background: linear-gradient(135deg, #a5b4fc, #e879f9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1; margin-bottom: 1rem;">
            Intelligent Document<br>Generation for Product Teams
          </h1>
          <p style="color: #94a3b8; font-size: 1.15rem; margin-top: 1rem; margin-bottom: 2rem; line-height: 1.6; max-width: 90%;">
            Transform stakeholder discussions into professional BRDs, FRDs & Agile artifacts in seconds. Experience the next generation of AI-driven product management tools.
          </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features row
        features = ["📄 BRD Generator", "📋 FRD Generator", "🎯 Agile Stories", "🔍 Gap Analysis", "⚠️ Risk Engine", "📥 PDF & DOCX Export"]
        st.markdown(" ".join(f'<span class="feature-pill" style="margin-bottom: 10px;">{f}</span>' for f in features), unsafe_allow_html=True)

    with col_auth:
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["🔐 Sign In", "✨ Create Account"])

        with tab_login:
            with st.form("login_form", border=True):
                st.markdown("<h4 style='color: white; margin-bottom: 1rem;'>Welcome Back</h4>", unsafe_allow_html=True)
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                remember_me = st.checkbox("Keep me signed in (24 hours)", value=True)
                submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

                if submitted:
                    if email and password:
                        ok, user, msg = login_user(email, password)
                        if ok:
                            # Create persistent auth token
                            if remember_me:
                                auth_token = create_auth_cookie(user["id"], user["email"])
                                SimpleAuthCache.cache_auth_token(auth_token)
                                st.session_state.auth_token = auth_token
                            
                            st.session_state.user = user
                            st.session_state.auth_success = msg
                            st.toast("✅ " + msg)
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                    else:
                        st.warning("Please fill in all fields.")

        with tab_register:
            with st.form("register_form", border=True):
                st.markdown("<h4 style='color: white; margin-bottom: 1rem;'>Start Building for Free</h4>", unsafe_allow_html=True)
                reg_name  = st.text_input("Full Name", placeholder="Aditya Rawat")
                reg_email = st.text_input("Email", placeholder="you@example.com")
                reg_pass  = st.text_input("Password (min 8 chars)", type="password")
                reg_pass2 = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Create Account →", use_container_width=True, type="primary")

                if submitted:
                    if not all([reg_name, reg_email, reg_pass, reg_pass2]):
                        st.warning("Please fill in all fields.")
                    elif reg_pass != reg_pass2:
                        st.error("❌ Passwords do not match.")
                    else:
                        ok, msg = register_user(reg_email, reg_pass, reg_name)
                        if ok:
                            st.success(f"✅ {msg} Please sign in.")
                        else:
                            st.error(f"❌ {msg}")

    st.markdown("---")
    st.caption("🔒 Persistent login: 24-hour session | Free tier: 3 documents/month | Pro: Unlimited | Your data is never stored beyond processing")
