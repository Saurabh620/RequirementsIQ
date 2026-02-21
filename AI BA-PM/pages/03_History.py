"""
Page: Document History
Lists all past documents with quick-view and navigation links.
"""
import streamlit as st
from services.document_service import get_user_documents, get_document

st.set_page_config(page_title="History — RequirementIQ", page_icon="📁", layout="wide")

if not st.session_state.get("user"):
    st.warning("Please log in.")
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

from utils.ui_theme import inject_theme
inject_theme()

st.markdown("""
<div class="admin-header" style="padding: 1.5rem; margin-bottom: 2rem;">
  <h1 style="font-size: 2.2rem; margin-bottom: 0.5rem; color: #f8fafc;">📁 Document History</h1>
  <p style="color: #a5b4fc; font-size: 1rem; margin: 0;">Review, search, and export your previously generated documents.</p>
</div>
""", unsafe_allow_html=True)

documents = get_user_documents(user["id"], limit=50)

if not documents:
    st.info("You haven't generated any documents yet.")
    if st.button("⚡ Generate Your First Document", type="primary"):
        st.switch_page("pages/01_Generate.py")
    st.stop()

with st.container(border=True):
    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        domain_filter = st.selectbox("Filter by Domain", ["All", "generic", "saas", "bfsi", "healthcare"], label_visibility="collapsed")
    with col_f2:
        search = st.text_input("Search by title", placeholder="Search documents...", label_visibility="collapsed")

filtered = documents
if domain_filter != "All":
    filtered = [d for d in filtered if d["domain"] == domain_filter]
if search:
    filtered = [d for d in filtered if search.lower() in (d["title"] or "").lower()]

st.caption(f"Showing **{len(filtered)}** of **{len(documents)}** documents")
st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

STATUS_ICONS = {"completed": "✅", "partial": "⚠️", "failed": "❌", "processing": "🔄", "pending": "⏳"}
DOMAIN_ICONS = {"saas": "☁️", "bfsi": "🏦", "healthcare": "🏥", "generic": "🌐"}

for doc in filtered:
    status_icon = STATUS_ICONS.get(doc["status"], "❓")
    domain_icon = DOMAIN_ICONS.get(doc["domain"], "🌐")
    score = doc.get("score") or 0
    score_color = "green" if score >= 80 else "orange" if score >= 50 else "red"

    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
        with c1:
            st.markdown(f"**{status_icon} {doc['title']}**")
            st.caption(f"{domain_icon} {doc['domain'].upper()} | Types: {doc['types']} | {doc['created'][:16]}")
        with c2:
            st.markdown(f"<div style='text-align:center;padding:4px;color:{score_color};font-weight:700'>{score}%</div>", unsafe_allow_html=True)
        with c3:
            st.caption(doc["status"].upper())
        with c4:
            if st.button("Open →", key=f"view_{doc['id']}", use_container_width=True):
                full_doc = get_document(doc["id"], user["id"])
                st.session_state["current_doc"] = full_doc
                st.session_state["current_doc_id"] = doc["id"]
                st.switch_page("pages/02_Document.py")
