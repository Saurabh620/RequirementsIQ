"""
Page: Generate Document
Core workflow: Upload/Paste/Voice → Configure → Generate → View Results
"""
import time
import streamlit as st
from services.auth_service import can_generate, increment_doc_count
from services.file_parser import parse_uploaded_file, parse_pasted_text, validate_file_size
from services.document_service import save_document, save_pipeline_result, get_document
from ai.orchestrator import run_pipeline
from utils.domain_classifier import classify_domain
from utils.voice_transcriber import transcribe_audio, SUPPORTED_LANGUAGES
from utils.professional_button import professional_button

st.set_page_config(page_title="Generate — RequirementIQ", page_icon="⚡", layout="wide")

# Auth gate - ensure user is authenticated
if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Please log in to continue.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

user = st.session_state.user

# Safety check (should not reach here if auth gate works, but just in case)
if user is None:
    st.error("Authentication error. Please log in again.")
    if st.button("Return to Login"):
        st.session_state.user = None
        st.switch_page("app.py")
    st.stop()

# ── CSS ───────────────────────────────────────────────────────
from utils.ui_theme import inject_theme
inject_theme()

# ── Header ────────────────────────────────────────────────────
col_hdr, col_quota = st.columns([2, 1], gap="large")
with col_hdr:
    st.markdown("""
    <div class="gen-header">
      <h2>⚡ Generate Requirements Document</h2>
      <p>Upload a file, paste notes, or <b>record your voice</b> to generate artifacts</p>
    </div>
    """, unsafe_allow_html=True)

# Quota indicator
docs_left = user["docs_limit"] - user["docs_used"]
quota_pct = user["docs_used"] / max(user["docs_limit"], 1)

with col_quota:
    st.markdown(f'<div class="quota-bar" style="margin-top: 0.5rem; padding: 1rem; margin-bottom: 0.5rem;">📊 <b>{user["docs_used"]}/{user["docs_limit"]}</b> used — <b>{docs_left} remaining</b></div>', unsafe_allow_html=True)
    st.progress(min(quota_pct, 1.0))

if docs_left <= 0:
    st.error("🚫 You've reached your monthly document limit. Upgrade to Pro for unlimited generation.")
    if st.button("🚀 Upgrade to Pro"):
        st.switch_page("pages/04_Settings.py")
    st.stop()

st.divider()

st.markdown("<br>", unsafe_allow_html=True)

# SaaS Grid Layout setup
grid_left, grid_right = st.columns([1.5, 1], gap="large")

# Initialize voice state
if "voice_transcribed_text" not in st.session_state:
    st.session_state.voice_transcribed_text = ""
    
raw_text = ""
input_type = "paste"

# ── Step 1: Input ─────────────────────────────────────────────
with grid_left:
    with st.container(border=True):
        st.markdown('<p class="step-label">Step 1 — Provide Input</p>', unsafe_allow_html=True)

        input_tab, upload_tab, voice_tab = st.tabs([
            "📋 Paste Text",
            "📎 Upload File",
            "🎤 Record Voice"
        ])

        with input_tab:
            pasted = st.text_area(
                "Paste stakeholder notes, meeting transcript, or requirements",
                height=250,
                placeholder="Example:\\nWe need a CRM system for our 50-person sales team...\\nKey features: lead tracking, pipeline management, email integration...",
                label_visibility="collapsed"
            )
    if pasted:
        try:
            raw_text, input_type = parse_pasted_text(pasted)
            st.caption(f"✅ {len(raw_text):,} characters detected")
        except ValueError as e:
            st.error(str(e))

with upload_tab:
    uploaded = st.file_uploader("Upload .txt or .docx file", type=["txt", "docx"], label_visibility="collapsed")
    if uploaded:
        if not validate_file_size(uploaded):
            st.error("❌ File exceeds 50MB limit.")
        else:
            try:
                raw_text, input_type = parse_uploaded_file(uploaded, uploaded.name)
                st.success(f"✅ Parsed **{uploaded.name}** — {len(raw_text):,} characters")
                with st.expander("Preview extracted text"):
                    st.text(raw_text[:500] + ("..." if len(raw_text) > 500 else ""))
            except ValueError as e:
                st.error(str(e))

# ── Tab 3: Voice Recording ─────────────────────────────────
with voice_tab:
    col_lang, _ = st.columns([2, 3])
    with col_lang:
        lang_label = st.selectbox("🌐 Language", options=list(SUPPORTED_LANGUAGES.keys()), index=0)
    selected_lang = SUPPORTED_LANGUAGES[lang_label]

    st.markdown("**🎤 Click the microphone below, speak your requirements, then click Transcribe:**")
    st.caption("Describe the system, stakeholders, features, and constraints. Works best for 10–120 second recordings.")

    # Safely handle audio_input if available
    if hasattr(st, 'audio_input'):
        audio_value = st.audio_input(
            label="Record your requirements",
            label_visibility="collapsed",
            key="voice_recorder"
        )
    else:
        st.warning("⚠️ Audio recording requires Streamlit 1.19.0+. Please update Streamlit.")
        audio_value = None

    if audio_value is not None:
        col_audio, col_ctrl = st.columns([3, 1])
        with col_audio:
            st.audio(audio_value, format="audio/wav")
        with col_ctrl:
            if st.button("🗑️ Clear Recording", use_container_width=True):
                st.session_state.voice_transcribed_text = ""
                # Streamlit audio_input doesn't have a direct clear method,
                # but clearing it from session state forces it to reset on rerun
                if "voice_recorder" in st.session_state:
                    del st.session_state["voice_recorder"]
                st.rerun()

        def transcribe_voice_recording():
            """Transcribe the voice recording using Google Speech API."""
            transcribed, status = transcribe_audio(audio_value.getvalue(), language=selected_lang)
            
            if status == "success" and transcribed:
                st.session_state.voice_transcribed_text = transcribed
                return transcribed
            elif status == "no_speech":
                raise ValueError("⚠️ No speech detected — please speak clearly closer to your mic and try again.")
            else:
                raise RuntimeError(f"❌ {status}")
        
        if professional_button(
            button_id="transcribe_voice_btn",
            label="🔄 Transcribe Now",
            on_click=transcribe_voice_recording,
            button_type="primary",
            use_container_width=True,
            show_progress_bar=False,
            success_message="✅ Transcription complete!",
        ):
            transcribed = transcribe_voice_recording()
            if transcribed:
                st.success(f"📝 {len(transcribed):,} characters ready for generation")

    if st.session_state.voice_transcribed_text:
        st.markdown("**📝 Review & Edit Transcription** *(correct any errors before generating)*")
        edited = st.text_area(
            "Transcribed text",
            value=st.session_state.voice_transcribed_text,
            height=200,
            label_visibility="collapsed",
            key="voice_text_editor"
        )
        if edited:
            raw_text  = edited.strip()
            input_type = "paste"
            st.caption(f"✅ {len(raw_text):,} characters ready for generation")
        col_clr, _ = st.columns([1, 4])
        with col_clr:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.voice_transcribed_text = ""
                st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center;padding:2rem;color:#475569;border:1px dashed rgba(255,255,255,0.1);border-radius:10px;margin-top:1rem">
          <div style="font-size:2.5rem">🎤</div>
          <div style="font-size:0.9rem;margin-top:0.5rem">Record audio above → click <b>Transcribe Now</b></div>
          <div style="font-size:0.8rem;color:#cbd5e1;margin-top:0.3rem">Supports English, Hindi, Gujarati, Tamil &amp; more</div>
        </div>
        """, unsafe_allow_html=True)

# ── Step 2: Configure ─────────────────────────────────────────
with grid_right:
    with st.container(border=True):
        st.markdown('<p class="step-label">Step 2 — Configure Pipeline</p>', unsafe_allow_html=True)

        auto_domain = classify_domain(raw_text) if raw_text else "generic"
        domain = st.selectbox(
            "Industry Domain",
            options=["auto", "generic", "saas", "bfsi", "healthcare"],
            index=0,
            format_func=lambda x: {
                "auto": f"🤖 Auto-detect (detected: {auto_domain})",
                "generic": "🌐 Generic Software",
                "saas": "☁️ SaaS / Cloud Product",
                "bfsi": "🏦 BFSI (Banking/Finance/Insurance)",
                "healthcare": "🏥 Healthcare IT"
            }.get(x, x)
        )
        resolved_domain = auto_domain if domain == "auto" else domain

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        output_types = st.multiselect(
            "Documents to Generate",
            options=["brd", "frd", "agile"],
            default=["brd", "frd", "agile"],
            format_func=lambda x: {"brd": "📄 BRD", "frd": "📋 FRD", "agile": "🎯 Agile Stories"}.get(x, x)
        )

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        doc_title = st.text_input("Document Title (optional)", placeholder="e.g. CRM Platform — Q2 Requirements")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # ── Step 3: Generate ──────────────────────────────────────────
    with st.container(border=True):
        st.markdown('<p class="step-label">Step 3 — Execute</p>', unsafe_allow_html=True)

        if not raw_text:
            st.info("💡 Provide input in Step 1 to begin.")

        # ── Professional button with SaaS behavior ──────────────────
        def execute_generate():
            """Execute the document generation pipeline."""
            # Validate inputs
            if not raw_text:
                raise ValueError("Please provide input text first.")
            if not output_types:
                raise ValueError("Please select at least one document type.")

            # Check permissions
            can_gen, msg = can_generate(user)
            if not can_gen:
                raise PermissionError(msg)

            # Save document record
            doc_id = save_document(
                user_id=user["id"], raw_input_text=raw_text, input_type=input_type,
                domain=resolved_domain, output_types=output_types, title=doc_title or None
            )

            # Run pipeline
            result = run_pipeline(
                raw_text=raw_text,
                domain=resolved_domain,
                output_types=output_types,
                user_email=user.get("email", "system"),
                user_name=user.get("full_name", "User")
            )

            # Save results
            save_pipeline_result(doc_id, user["id"], result, gen_start=time.time())
            increment_doc_count(user["id"])

            # Update quota in session (now safe - running on main thread)
            if st.session_state.user is not None and isinstance(st.session_state.user, dict):
                if "docs_used" in st.session_state.user:
                    st.session_state.user["docs_used"] += 1
            
            # Store for document viewer
            st.session_state["current_doc_id"] = doc_id
            st.session_state["current_doc"] = get_document(doc_id, user["id"])

            # Show any warnings
            if result.errors:
                st.warning(f"⚠️ Generated with {len(result.errors)} warning(s): {'; '.join(result.errors[:2])}")

            st.balloons()
            return doc_id

        # Render professional button
        if professional_button(
            button_id="generate_documents_main",
            label="⚡ Generate Documents",
            on_click=execute_generate,
            button_type="primary",
            use_container_width=True,
            show_progress_bar=False,  # Disable threading to keep on main thread
            success_message="✅ Documents generated successfully!",
        ):
            # Task completed - show next action
            if st.button("📄 View Generated Document →", type="primary", use_container_width=True):
                st.switch_page("pages/02_Document.py")
