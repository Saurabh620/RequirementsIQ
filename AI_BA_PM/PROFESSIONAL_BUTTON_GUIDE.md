"""
Integration Guide: Professional SaaS Button Behavior
=====================================================

This guide shows how to use the professional_button utility to enhance your Streamlit app
with production-grade button interactions.

KEY FEATURES:
✓ Prevents duplicate clicks via session_state
✓ Auto-disables button during execution
✓ Shows spinner immediately
✓ Shows progress bar for tasks > 2 seconds
✓ Displays success toast with execution time
✓ Subtle confirmation animation
✓ Clean, minimal UI

BASIC USAGE:
============

from utils.professional_button import professional_button
import time

def my_task():
    time.sleep(1)
    return "Task completed"

# Simple button
if professional_button(
    button_id="my_action",
    label="🚀 Do Something",
    on_click=my_task,
):
    st.success("Task done!")

---

ADVANCED USAGE WITH ARGUMENTS:
=============================

def process_data(name, count):
    time.sleep(2)
    return f"Processed {count} items for {name}"

if professional_button(
    button_id="process_btn",
    label="⚡ Process Data",
    on_click=process_data,
    "John",  # positional arg
    count=100,  # keyword arg
    button_type="primary",
    use_container_width=True,
    show_progress_bar=True,
    progress_threshold=2.0,  # Show progress if > 2 seconds
    success_message="✨ Data processing complete!",
):
    st.info("Ready for next step")

---

REAL WORLD EXAMPLE (Document Generation):
==========================================

from utils.professional_button import professional_button
from ai.orchestrator import run_pipeline
import time

# This is the refactored version of your Generate.py button:

def generate_documents():
    '''Task that runs pipeline'''
    doc_id = save_document(...)
    result = run_pipeline(
        raw_text=raw_text,
        domain=resolved_domain,
        output_types=output_types,
    )
    save_pipeline_result(doc_id, user["id"], result)
    return doc_id

# Render professional button
if professional_button(
    button_id="generate_docs_btn",
    label="⚡ Generate Documents",
    on_click=generate_documents,
    button_type="primary",
    use_container_width=True,
    show_progress_bar=True,
    progress_threshold=2.0,
    success_message=f"✅ Documents generated in {exec_time:.1f}s",
):
    # Task completed successfully
    st.session_state["current_doc_id"] = doc_id
    st.balloons()
    if st.button("📄 View Generated Document →"):
        st.switch_page("pages/02_Document.py")

---

INTEGRATION PATTERNS:
====================

Pattern 1: Simple Action
------------------------
if professional_button("btn_id", "Label", action_func):
    st.success("Done!")

Pattern 2: Action with Return Value
-----------------------------------
result = professional_button(
    "btn_id", 
    "Label",
    expensive_function,
    arg1, arg2,
    kwarg1=value1
)

Pattern 3: Conditional Button
-----------------------------
if condition:
    if professional_button("btn_id", "Label", task):
        st.success("Action completed!")

Pattern 4: Button with Custom Success Message
---------------------------------------------
if professional_button(
    "btn_id",
    "Label",
    task,
    success_message="✨ Custom message with stats!",
):
    pass

---

BEST PRACTICES:
===============

1. UNIQUE BUTTON IDs:
   - Use descriptive, snake_case IDs
   - Ensure uniqueness within page
   - Pattern: "{action}_{object}_{context}_btn"
   - Good:   "generate_documents_btn", "export_to_pdf_btn"
   - Bad:    "btn1", "button", "submit"

2. TASK FUNCTIONS:
   - Keep on_click functions clean and focused
   - Return meaningful values
   - Handle errors inside on_click for better UX
   - Keep long operations > 2 seconds visible

3. SUCCESS MESSAGES:
   - Use success_message for app-specific feedback
   - Include relevant metrics (time, count, etc.)
   - Short and actionable (< 80 chars)
   - Example: "✅ 5 documents generated in 3.2s"

4. PROGRESS THRESHOLD:
   - Default 2.0 seconds is good for most cases
   - Reduce to 0.5s for fast-feeling apps
   - Increase to 5s+ only for very heavy operations

5. DISABLE STATES:
   - Always use conditional disabling on button()
   - Button auto-disables during execution
   - Additional checks handled via condition
   - Example: disabled=not raw_text or not output_types

---

MIGRATING EXISTING BUTTONS:
===========================

Before:
-------
if st.button("Generate", type="primary", use_container_width=True):
    with st.spinner("Processing..."):
        result = expensive_task()
    st.success("Done!")

After:
------
if professional_button(
    button_id="generate_btn",
    label="Generate",
    on_click=expensive_task,
    button_type="primary",
    use_container_width=True,
    success_message=f"✅ Task complete!",
):
    st.info("Ready for next step")

---

COMMON PATTERNS IN REQUIREMENTSIQ:
==================================

1. Voice Transcription Button:
   if professional_button(
       "transcribe_voice_btn",
       "🔄 Transcribe Now",
       transcribe_audio,
       audio_value.getvalue(),
       language=selected_lang,
       button_type="primary",
   ):
       st.session_state.voice_transcribed_text = transcribed_text
       st.success("✅ Transcription complete!")

2. Document Generation Button:
   if professional_button(
       "generate_docs_btn",
       "⚡ Generate Documents",
       generate_documents,
       show_progress_bar=True,
       progress_threshold=2.0,
   ):
       st.balloons()
       st.success("Move to Document Viewer →")

3. Export Button:
   if professional_button(
       "export_pdf_btn",
       "📥 Export as PDF",
       generate_pdf,
       doc_id,
       user["id"],
       success_message="✅ PDF generated!",
   ):
       st.download_button(...)

---

TROUBLESHOOTING:
================

Q: Button stays disabled after error?
A: on_click should handle its own errors gracefully

Q: Success message not showing?
A: Ensure on_click doesn't raise exceptions

Q: Multiple buttons not working?
A: Check button_id is unique per button

Q: Progress bar not showing?
A: Task needs to be > progress_threshold (default 2s)
   Reduce progress_threshold parameter if needed

---

For full source code, see: utils/professional_button.py
"""

# This is documentation only - no executable code
