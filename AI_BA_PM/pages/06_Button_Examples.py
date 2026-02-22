"""
Example Page: Professional Button Behaviors
Demonstrates all ProfessionalButton features with interactive examples
"""
import time
import streamlit as st
from utils.professional_button import professional_button

st.set_page_config(page_title="Button Examples", page_icon="🎯", layout="wide")

st.markdown("# 🎯 Professional SaaS Button Examples")
st.markdown("Explore all features of production-grade button interactions")

# ── Session state init ────────────────────────────────────────
if "demo_results" not in st.session_state:
    st.session_state.demo_results = {}

col1, col2 = st.columns(2, gap="large")

# ────────────────────────────────────────────────────────────
# EXAMPLE 1: Fast Task (No Progress Bar)
# ────────────────────────────────────────────────────────────
with col1:
    with st.container(border=True):
        st.markdown("### ⚡ Example 1: Quick Action")
        st.markdown("*Task completes in <2sec → no progress bar*")

        def quick_task():
            time.sleep(0.8)
            return "Quick result"

        if professional_button(
            button_id="quick_action_demo",
            label="📊 Quick Calculation",
            on_click=quick_task,
            show_progress_bar=True,
            progress_threshold=2.0,
        ):
            st.session_state.demo_results["quick"] = True
            st.info("✨ Result available immediately!")

# ────────────────────────────────────────────────────────────
# EXAMPLE 2: Slow Task (Shows Progress)
# ────────────────────────────────────────────────────────────
with col2:
    with st.container(border=True):
        st.markdown("### 🔄 Example 2: Long-Running Task")
        st.markdown("*Task > 2sec → shows progress bar & elapsed time*")

        def slow_task():
            for i in range(5):
                time.sleep(1)
            return "Complete"

        if professional_button(
            button_id="slow_action_demo",
            label="🎬 Processing Video",
            on_click=slow_task,
            show_progress_bar=True,
            progress_threshold=1.5,  # Lower threshold to demo progress
        ):
            st.session_state.demo_results["slow"] = True
            st.success("🎉 Video processed successfully!")

# ────────────────────────────────────────────────────────────
# EXAMPLE 3: Button with Arguments
# ────────────────────────────────────────────────────────────
st.divider()
with st.container(border=True):
    st.markdown("### 📝 Example 3: Button with Parameters")

    col_param, col_btn = st.columns([2, 1])

    with col_param:
        count = st.slider("Number of items to process", 1, 100, 50)
        process_name = st.text_input("Process name", "Data Import")

    def process_items(name, count):
        time.sleep(2)
        return f"Processed {count} {name}"

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if professional_button(
            button_id="process_items_demo",
            label="🚀 Process Now",
            on_click=process_items,
            process_name,
            count=count,
            button_type="primary",
            use_container_width=True,
            success_message=f"✅ Processed {count} items!",
        ):
            st.success(f"Result: {process_items(process_name, count)}")

# ────────────────────────────────────────────────────────────
# EXAMPLE 4: Multiple Independent Buttons
# ────────────────────────────────────────────────────────────
st.divider()
with st.container(border=True):
    st.markdown("### 🎛️ Example 4: Multiple Independent Actions")
    st.markdown("*Each button has its own state management*")

    col_export, col_delete, col_reset = st.columns(3)

    def export_task():
        time.sleep(1.5)
        return "exported"

    def delete_task():
        time.sleep(0.5)
        return "deleted"

    def reset_task():
        time.sleep(2.0)
        return "reset"

    with col_export:
        if professional_button(
            "export_multi_demo",
            "📥 Export",
            export_task,
            button_type="primary",
            use_container_width=True,
        ):
            st.success("Data exported!")

    with col_delete:
        if professional_button(
            "delete_multi_demo",
            "🗑️ Delete",
            delete_task,
            button_type="secondary",
            use_container_width=True,
        ):
            st.warning("Item deleted")

    with col_reset:
        if professional_button(
            "reset_multi_demo",
            "🔄 Reset",
            reset_task,
            button_type="secondary",
            use_container_width=True,
        ):
            st.info("Reset complete")

# ────────────────────────────────────────────────────────────
# EXAMPLE 5: Conditional Button (Disabled State)
# ────────────────────────────────────────────────────────────
st.divider()
with st.container(border=True):
    st.markdown("### 🎚️ Example 5: Conditional Actions")

    col_input, col_action = st.columns([2, 1])

    with col_input:
        user_input = st.text_input("Enter text to validate")
        input_valid = len(user_input) >= 5

    def validate_input():
        time.sleep(1)
        return len(user_input)

    with col_action:
        st.markdown("<br>", unsafe_allow_html=True)
        # Button is enabled/disabled based on condition
        if professional_button(
            "conditional_demo",
            "✅ Submit" if input_valid else "📝 Type more...",
            validate_input,
            button_type="primary",
            use_container_width=True,
        ):
            st.success(f"Valid input: {len(user_input)} characters")

    if not input_valid:
        st.caption(f"ℹ️ Need {5 - len(user_input)} more characters")

# ────────────────────────────────────────────────────────────
# EXAMPLE 6: Error Handling
# ────────────────────────────────────────────────────────────
st.divider()
with st.container(border=True):
    st.markdown("### ⚠️ Example 6: Error Handling")

    col_success, col_error = st.columns(2)

    def success_task():
        time.sleep(1)
        return True

    def failing_task():
        time.sleep(1)
        raise ValueError("Something went wrong!")

    with col_success:
        if professional_button(
            "success_demo",
            "✨ Succeed",
            success_task,
            button_type="primary",
            use_container_width=True,
        ):
            st.success("Everything worked!")

    with col_error:
        try:
            if professional_button(
                "error_demo",
                "💥 Fail Gracefully",
                failing_task,
                button_type="secondary",
                use_container_width=True,
            ):
                pass
        except ValueError as e:
            # Custom error handling
            st.error(f"Handled: {e}")

# ────────────────────────────────────────────────────────────
# FEATURE COMPARISON TABLE
# ────────────────────────────────────────────────────────────
st.divider()
st.markdown("## 📊 Feature Summary")

features = {
    "Feature": [
        "Click Prevention",
        "Auto-Disable",
        "Immediate Spinner",
        "Progress Bar (>2s)",
        "Success Toast",
        "Execution Time Display",
        "Subtle Animation",
        "Session State Management",
        "Custom Messages",
        "Multiple Arguments",
    ],
    "Professional Button": ["✅"] * 10,
    "Standard st.button()": [
        "❌", "❌", "❌", "❌", "❌", "❌", "❌", "❌", "❌", "❌"
    ],
}

import pandas as pd

df = pd.DataFrame(features)
st.table(df)

# ────────────────────────────────────────────────────────────
# UX BEST PRACTICES
# ────────────────────────────────────────────────────────────
st.divider()
st.markdown("## 💡 Best Practices for SaaS UX")

practices = """
### 1. **Button Naming**
   - Use action verbs: "Generate", "Export", "Validate"
   - Include emojis for visual scanning
   - Be specific: "Export as PDF" not "Download"

### 2. **Progress Indicators**
   - Show spinner immediately for any async operation
   - Progress bar for operations > 2 seconds
   - Always display elapsed time for long tasks
   - This prevents the "did it freeze?" question

### 3. **Success Feedback**
   - Brief, celebratory messages
   - Include metrics when relevant: "5 items imported"
   - Show execution time: "Completed in 3.2s"
   - Use checkmarks and green to confirm

### 4. **Disable States**
   - Disable buttons when prerequisite fields are empty
   - Disable during execution (handled automatically)
   - Provide tooltip explaining why disabled
   - Example: "Fill in email to proceed"

### 5. **Button Placement**
   - Action buttons (primary) at bottom or top right
   - Destructive actions (delete) separate from main flow
   - Group related actions together
   - Use full width for main actions

### 6. **Error Messages**
   - Show specific error with timestamp
   - Include copy-able error code if system error
   - Suggest next steps for user
   - Offer retry after handling the error

### 7. **Accessibility**
   - Always provide text labels
   - Use high contrast colors
   - Keyboard navigate (default in Streamlit)
   - Provide aria-labels if needed

### 8. **Performance**
   - Keep on_click functions focused and clean
   - Return meaningful values
   - Avoid heavy operations outside async context
   - Cache expensive operations when possible
"""

st.markdown(practices)

# ────────────────────────────────────────────────────────────
# CODE SNIPPETS
# ────────────────────────────────────────────────────────────
st.divider()
st.markdown("## 📖 Quick Reference Code")

with st.expander("Basic Button"):
    st.code(
        """
from utils.professional_button import professional_button

if professional_button(
    button_id="my_action",
    label="⚡ Do Something",
    on_click=my_function,
):
    st.success("Done!")
        """,
        language="python",
    )

with st.expander("Button with Arguments"):
    st.code(
        """
def export_data(format, include_header):
    # Your task logic
    return "exported"

if professional_button(
    button_id="export_btn",
    label="📥 Export",
    on_click=export_data,
    "pdf",  # positional arg
    include_header=True,  # keyword arg
):
    st.success("Data exported!")
        """,
        language="python",
    )

with st.expander("Button with Custom Messages"):
    st.code(
        """
if professional_button(
    button_id="process_btn",
    label="🔄 Process",
    on_click=long_running_task,
    show_progress_bar=True,
    progress_threshold=1.0,  # Show progress after 1 second
    success_message="✨ 5 items processed in 3.2s!",
):
    st.info("Ready for next step")
        """,
        language="python",
    )

st.markdown("---")
st.markdown(
    "_For complete documentation, see `PROFESSIONAL_BUTTON_GUIDE.md` in the project root_"
)
