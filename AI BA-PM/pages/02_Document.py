"""
Page: Document Viewer
Tabbed display of BRD / FRD / Agile artifacts + Gap & Risk panels + Export.
"""
import json
import streamlit as st
from services.document_service import get_document, get_user_documents
from services.export_service import generate_pdf, generate_docx

st.set_page_config(page_title="Document — RequirementIQ", page_icon="📄", layout="wide")

if not st.session_state.get("user"):
    st.warning("Please log in.")
    if st.button("Login"):
        st.switch_page("app.py")
    st.stop()

user = st.session_state.user

from utils.ui_theme import inject_theme
inject_theme()

# ── Load Document ─────────────────────────────────────────────
doc = None
# Try session first (just generated), then let user pick from history
if "current_doc" in st.session_state and st.session_state["current_doc"]:
    doc = st.session_state["current_doc"]

# Allow switching document
st.sidebar.markdown("### 📁 My Documents")
all_docs = get_user_documents(user["id"], limit=10)
if all_docs:
    options = {d["title"]: d["id"] for d in all_docs}
    selected_title = st.sidebar.selectbox("Switch document", list(options.keys()),
                                           index=0 if doc and doc["id"] in options.values() else 0)
    selected_id = options[selected_title]
    if not doc or doc["id"] != selected_id:
        doc = get_document(selected_id, user["id"])
        st.session_state["current_doc"] = doc

if not doc:
    st.info("No document loaded. Generate one first!")
    if st.button("⚡ Generate Document"):
        st.switch_page("pages/01_Generate.py")
    st.stop()

# ── Document Header ───────────────────────────────────────────
score = doc.get("completeness_score", 0) or 0
score_color = "#34d399" if score >= 80 else "#fbbf24" if score >= 50 else "#f87171"

st.markdown(f"""
<div class="admin-header" style="padding: 1.5rem; margin-bottom: 2rem; display: flex; flex-direction: row; justify-content: space-between; align-items: center;">
  <div>
    <h1 style="font-size: 2.2rem; margin-bottom: 0.5rem; color: #f8fafc; margin-top: 0;">📄 {doc.get('title', 'Untitled Document')}</h1>
    <p style="color: #a5b4fc; font-size: 0.95rem; margin: 0;">
      Domain: <b>{doc.get('domain', 'generic').upper()}</b> &nbsp;|&nbsp; 
      Status: <b>{doc.get('status', 'unknown').upper()}</b> &nbsp;|&nbsp; 
      Generated: {doc.get('created_at', '')[:16]}
    </p>
  </div>
  <div style='text-align:center;background:rgba(15,23,42,0.6);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:0.8rem 1.5rem'>
    <span style='font-size:2rem;font-weight:800;color:{score_color};line-height:1;'>{score}%</span><br>
    <span style='color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;'>Completeness</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Main Tabs ─────────────────────────────────────────────────
tab_labels = []
if doc.get("brd"):    tab_labels.append("📄 BRD")
if doc.get("frd"):    tab_labels.append("📋 FRD")
if doc.get("agile"):  tab_labels.append("🎯 Agile")
tab_labels += ["🔍 Gap Analysis", "⚠️ Risk Register", "📥 Export"]

tabs = st.tabs(tab_labels)
tab_idx = 0

# ── BRD Tab ───────────────────────────────────────────────────
if doc.get("brd"):
    with tabs[tab_idx]:
        brd = doc["brd"]
        st.markdown("### Business Requirements Document")

        def conf_badge(c): return f'<span class="confidence-{c}">● {c.title()} Confidence</span>'

        if brd.get("project_name"):
            st.markdown(f"#### 🏷️ Project: {brd['project_name']}")

        # 1. Document Control
        if brd.get("document_control"):
            with st.expander("📄 Document Control", expanded=False):
                dc_list = [
                    {"Field": k.replace("_", " ").title(), "Details": str(v)}
                    for k, v in brd["document_control"].items()
                ]
                st.table(dc_list)

        # 2. Executive Summary
        if brd.get("executive_summary", {}).get("content") not in (None, "INSUFFICIENT_DATA"):
            with st.expander("📌 Executive Summary", expanded=True):
                st.markdown(brd["executive_summary"]["content"])

        # 3. Business Objectives
        if brd.get("business_objectives"):
            with st.expander("🎯 Business Objectives"):
                for obj in brd["business_objectives"]: st.markdown(f"• {obj}")
                if brd.get("success_criteria"):
                    st.markdown("**Success Criteria:**")
                    for m in brd["success_criteria"]: st.markdown(f"◦ {m}")

        # 4. Problem Statement
        if brd.get("problem_statement", {}).get("content") not in (None, "INSUFFICIENT_DATA"):
            with st.expander("❓ Problem Statement", expanded=True):
                st.markdown(brd["problem_statement"]["content"])

        # 5. Scope
        col1, col2 = st.columns(2)
        with col1:
            if brd.get("scope_in"):
                with st.expander("✅ Scope — In"):
                    for s in brd["scope_in"]: st.markdown(f"• {s}")
        with col2:
            if brd.get("scope_out"):
                with st.expander("❌ Scope — Out"):
                    for s in brd["scope_out"]: st.markdown(f"• {s}")

        # 6. Stakeholders
        valid_stakeholders = [
            s for s in brd.get("stakeholders", [])
            if s.get("name","") not in ("", "INSUFFICIENT_DATA")
            and s.get("role","") not in ("", "INSUFFICIENT_DATA")
        ]
        if valid_stakeholders:
            with st.expander("👥 Stakeholders"):
                st.table(valid_stakeholders)

        # 7. Business Requirements
        if brd.get("business_requirements"):
            with st.expander("🏢 Business Requirements", expanded=True):
                st.table(brd["business_requirements"])

        # 8. Functional Requirements
        if brd.get("functional_requirements"):
            with st.expander("⚙️ Functional Requirements", expanded=True):
                st.table(brd["functional_requirements"])

        # 9. Non-Functional Requirements
        if brd.get("non_functional_requirements"):
            with st.expander("🛡️ Non-Functional Requirements"):
                for k, v in brd["non_functional_requirements"].items():
                    st.markdown(f"**{k.title()}**: {v}")

        # 10, 11, 12, 14. Assumptions, Constraints, Dependencies, Acceptance Criteria
        acs_col1, acs_col2 = st.columns(2)
        with acs_col1:
            if brd.get("assumptions"):
                with st.expander("🤔 Assumptions"):
                    for a in brd["assumptions"]: st.markdown(f"• {a}")
            if brd.get("constraints"):
                with st.expander("🚧 Constraints"):
                    for c in brd["constraints"]: st.markdown(f"• {c}")
        with acs_col2:
            if brd.get("dependencies"):
                with st.expander("🔗 Dependencies"):
                    for d in brd["dependencies"]: st.markdown(f"• {d}")
            if brd.get("acceptance_criteria"):
                with st.expander("✅ Acceptance Criteria"):
                    for ac in brd["acceptance_criteria"]: st.markdown(f"• {ac}")

        # 13. Risks
        if brd.get("risks"):
            with st.expander("⚠️ Risks & Mitigation"):
                st.table(brd["risks"])

        # 15. Timeline / Milestones
        if brd.get("timeline_milestones"):
            with st.expander("⏳ Timeline / Milestones"):
                st.table(brd["timeline_milestones"])

    tab_idx += 1

# ── FRD Tab ───────────────────────────────────────────────────
if doc.get("frd"):
    with tabs[tab_idx]:
        frd = doc["frd"]
        st.markdown("### Functional Requirements Document")

        if frd.get("system_overview", {}).get("content") not in (None, "INSUFFICIENT_DATA"):
            with st.expander("🖥️ System Overview", expanded=True):
                st.markdown(frd["system_overview"]["content"])

        st.markdown("#### Functional Requirements")
        for fr in frd.get("functional_requirements", []):
            priority_colors = {"Must": "🔴", "Should": "🟡", "Could": "🟢", "Won't": "⚪"}
            icon = priority_colors.get(fr.get("priority", "Should"), "🔵")
            with st.expander(f"{icon} {fr.get('id','')}: {fr.get('title','')}"):
                st.markdown(fr.get("description",""))
                if fr.get("business_rule"):
                    st.info(f"**Business Rule:** {fr['business_rule']}")

        if frd.get("non_functional_requirements"):
            st.markdown("#### Non-Functional Requirements")
            nfr_data = [{"ID": n["id"], "Category": n["category"], "Requirement": n["requirement"], "Metric": n.get("metric","—")}
                        for n in frd["non_functional_requirements"]]
            st.table(nfr_data)

        if frd.get("integration_points"):
            with st.expander("🔗 Integration Points"):
                for ip in frd["integration_points"]:
                    st.markdown(f"**{ip['system']}** ({ip['type']}): {ip['description']}")
    tab_idx += 1

# ── Agile Tab ─────────────────────────────────────────────────
if doc.get("agile"):
    with tabs[tab_idx]:
        agile = doc["agile"]
        st.markdown("### Agile Artifacts")
        for epic in agile.get("epics", []):
            with st.expander(f"🚀 {epic.get('id','')} — {epic.get('title','')}"):
                st.markdown(f"*{epic.get('description','')}*")
                for story in epic.get("stories", []):
                    with st.container():
                        pts = story.get("story_points", "?")
                        prio = story.get("priority", "Should")
                        st.markdown(f"**{story.get('id','')}** [{pts} pts | {prio}]: {story.get('story','')}")
                        for ac in story.get("acceptance_criteria", []):
                            st.markdown(f"""
> **Given** {ac.get('given','')}  
> **When** {ac.get('when','')}  
> **Then** {ac.get('then','')}""")
                        st.divider()
    tab_idx += 1

# ── Gap Analysis Tab ──────────────────────────────────────────
with tabs[tab_idx]:
    gap = doc.get("gap")
    if not gap or not gap.get("gaps"):
        st.info("No gap analysis data available for this document.")
    else:
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Total Gaps", gap["total_gaps"])
        col_m2.metric("🔴 High", gap["high_count"])
        col_m3.metric("🟡 Medium", gap.get("medium_count",0))
        col_m4.metric("🟢 Low", gap.get("low_count",0))
        st.divider()
        for g in gap["gaps"]:
            sev = g.get("severity","LOW")
            st.markdown(f"""
<div class="artifact-card">
  <div style="display:flex;justify-content:space-between;margin-bottom:6px">
    <span class="section-title">{g.get('type','').replace('_',' ').title()}</span>
    <span class="severity-{sev}">{sev}</span>
  </div>
  <p style="color:#cbd5e1;margin:0 0 6px">{g.get('description','')}</p>
  <p style="color:#93c5fd;font-size:0.85rem;margin:0">💡 {g.get('recommendation','')}</p>
</div>""", unsafe_allow_html=True)
tab_idx += 1

# ── Risk Register Tab ─────────────────────────────────────────
with tabs[tab_idx]:
    risk = doc.get("risk")
    if not risk or not risk.get("risks"):
        st.info("No risk data available for this document.")
    else:
        c1, c2 = st.columns(2)
        c1.metric("Total Risks", risk["total_risks"])
        c2.metric("🔴 Critical", risk["critical_count"])
        st.divider()
        score_map = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
        for r in risk["risks"]:
            icon = score_map.get(r.get("risk_score","Medium"), "⚪")
            with st.expander(f"{icon} {r.get('title','')} [{r.get('category','')}]"):
                col_p, col_i, col_s = st.columns(3)
                col_p.metric("Probability", r.get("probability","—"))
                col_i.metric("Impact", r.get("impact","—"))
                col_s.metric("Score", r.get("risk_score","—"))
                st.markdown(r.get("description",""))
                st.info(f"**Mitigation:** {r.get('mitigation_strategy','')}")
tab_idx += 1

# ── Export Tab ────────────────────────────────────────────────
with tabs[tab_idx]:
    st.markdown("### 📥 Export Document")
    st.markdown('<div class="export-bar">', unsafe_allow_html=True)

    export_types = st.multiselect(
        "Include in export:",
        options=["brd", "frd", "agile", "gap_analysis", "risk_register"],
        default=["brd", "frd", "agile", "gap_analysis", "risk_register"],
        format_func=lambda x: {"brd":"📄 BRD","frd":"📋 FRD","agile":"🎯 Agile","gap_analysis":"🔍 Gap Analysis","risk_register":"⚠️ Risk Register"}.get(x,x)
    )

    export_data = {
        "title": doc["title"], "domain": doc["domain"], "created_at": doc["created_at"][:10],
        "brd":   doc.get("brd")   if "brd"           in export_types else None,
        "frd":   doc.get("frd")   if "frd"           in export_types else None,
        "agile": doc.get("agile") if "agile"         in export_types else None,
        "gap":   doc.get("gap")   if "gap_analysis"  in export_types else None,
        "risk":  doc.get("risk")  if "risk_register" in export_types else None,
    }

    col_pdf, col_docx = st.columns(2)
    with col_pdf:
        if st.button("📄 Generate PDF", use_container_width=True, type="primary"):
            with st.spinner("Rendering PDF..."):
                pdf_bytes = generate_pdf(export_data)
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name=f"{doc['title'].replace(' ','_')}_requirements.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    with col_docx:
        if st.button("📋 Generate DOCX", use_container_width=True):
            with st.spinner("Rendering DOCX..."):
                docx_bytes = generate_docx(export_data)
            st.download_button(
                label="⬇️ Download DOCX",
                data=docx_bytes,
                file_name=f"{doc['title'].replace(' ','_')}_requirements.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
    st.markdown('</div>', unsafe_allow_html=True)
