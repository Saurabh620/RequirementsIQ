# Professional SaaS Button System for Streamlit

A production-grade button interaction system that transforms your Streamlit app with professional dashboard behavior.

## 🎯 What You Get

✅ **Auto-disabled buttons** during execution (prevents duplicate clicks)  
✅ **Immediate spinner** showing UI is responsive  
✅ **Smart progress bar** appears for tasks >2 seconds  
✅ **Success toast** with execution time displayed  
✅ **Subtle animation feedback** for confirmation  
✅ **Session state management** built-in  
✅ **Zero complexity** to integrate  

## 📦 What's Included

```
utils/
├── professional_button.py          # Core button manager (main file)
├── professional_button_css.py      # CSS animations & styling
└── __init__.py

pages/
└── 06_Button_Examples.py           # Interactive demo page

Documentation:
├── PROFESSIONAL_BUTTON_GUIDE.md    # Complete reference guide
├── INTEGRATION_EXAMPLE_Generate.py # Real-world integration example
└── README_PROFESSIONAL_BUTTONS.md  # This file
```

## 🚀 Quick Start (3 Steps)

### Step 1: Add import to your page

```python
from utils.professional_button import professional_button
```

### Step 2: Create a task function

```python
def my_task():
    """Any long-running operation"""
    time.sleep(2)
    return result
```

### Step 3: Render professional button

```python
if professional_button(
    button_id="unique_button_name",
    label="⚡ Do Something",
    on_click=my_task,
):
    st.success("Task completed!")
```

That's it! You now have:
- Auto-disabled button ✅
- Spinner on click ✅  
- Progress bar after 2 seconds ✅
- Success message with time ✅
- No duplicate clicks ✅

## 💡 Usage Examples

### Basic Button (No Arguments)

```python
def export_data():
    time.sleep(1)
    return "exported"

if professional_button(
    button_id="export_btn",
    label="📥 Export",
    on_click=export_data,
):
    st.success("Data exported!")
```

### Button with Arguments

```python
def process_data(country, count):
    time.sleep(2)
    return f"Processed {count} items from {country}"

if professional_button(
    button_id="process_btn",
    label="⚡ Process",
    on_click=process_data,
    "USA",        # positional argument
    count=100,    # keyword argument
    button_type="primary",
    use_container_width=True,
):
    st.info("Ready for next step")
```

### Button with Custom Success Message

```python
if professional_button(
    button_id="scrape_btn",
    label="🔄 Scrape Website",
    on_click=scrape_function,
    show_progress_bar=True,
    progress_threshold=1.0,  # Show progress after 1 second
    success_message=f"✨ Scraped 500 items in 3.2s!",
):
    st.info("Data ready to download")
```

### Conditional Button (Disabled When Invalid)

```python
col_input, col_btn = st.columns([2, 1])

with col_input:
    email = st.text_input("Email")
    is_valid = "@" in email

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if professional_button(
        "submit_btn",
        "✅ Submit" if is_valid else "📝 Invalid Email",
        on_click=submit_function,
        button_type="primary",
    ):
        st.success("Submitted!")
```

## 🎨 Button Customization

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `button_id` | str | required | Unique identifier for state management |
| `label` | str | required | Button display text |
| `on_click` | callable | required | Function to execute |
| `button_type` | str | "primary" | "primary" \| "secondary" \| "tertiary" |
| `use_container_width` | bool | True | Span full width |
| `show_progress_bar` | bool | True | Show progress for long tasks |
| `progress_threshold` | float | 2.0 | Seconds before showing progress |
| `success_message` | str | None | Custom success text (shows time if None) |
| `*on_click_args` | tuple | - | Positional arguments for on_click |
| `**on_click_kwargs` | dict | - | Keyword arguments for on_click |

### Button Types

```python
# Primary - main action (blue gradient)
professional_button(..., button_type="primary")

# Secondary - alternative action (gray)
professional_button(..., button_type="secondary")

# Tertiary - minimal action
professional_button(..., button_type="tertiary")
```

## 🔧 Integration with Your App

### In pages/01_Generate.py

Replace this:
```python
if st.button("⚡ Generate Documents", type="primary", 
             use_container_width=True, 
             disabled=not raw_text or not output_types):
    with st.spinner("Processing..."):
        # ... lots of inline code ...
```

With this:
```python
def execute_generation():
    return run_pipeline(...)

if professional_button(
    "generate_docs_btn",
    "⚡ Generate Documents",
    on_click=execute_generation,
    show_progress_bar=True,
):
    st.balloons()
```

### Add CSS (Optional but Recommended)

In your `app.py` or any page:

```python
from utils.professional_button_css import inject_professional_button_css

# After inject_theme()
inject_professional_button_css()
```

This adds:
- Smooth animations for success toasts
- Subtle pulse when disabled
- Enhanced button styling
- Professional progress bar effects

## ⚙️ How It Works

### Session State Magic

The button uses session state keys to track execution:

```
_pb_processing_{button_id}  # Is button currently executing?
_pb_start_{button_id}       # When did execution start?
_pb_exec_time_{button_id}   # How long did it take?
```

This is all managed internally - you don't need to touch it.

### Execution Flow

```
User clicks button
    ↓
Button disabled, spinner starts
    ↓
Task executes (your on_click function)
    ↓
If > progress_threshold seconds: show progress bar
    ↓
Task completes
    ↓
Spinner disappears, success toast shows
    ↓
Execution time displayed (e.g., "✅ Completed in 3.2s")
```

### Error Handling

If your task raises an exception:

```python
def risky_task():
    if something_wrong:
        raise ValueError("Something went wrong!")
    return result

try:
    if professional_button("btn", "Try", risky_task):
        st.success("Done!")
except ValueError as e:
    st.error(f"Handled: {e}")
```

## 📚 Best Practices

### 1. Choose Clear Button IDs

```python
# ✅ Good - descriptive, unique, snake_case
professional_button("generate_documents_btn", ...)
professional_button("export_to_pdf_btn", ...)
professional_button("delete_user_btn", ...)

# ❌ Bad - vague, collides with other buttons
professional_button("btn", ...)
professional_button("click", ...)
```

### 2. Keep Tasks Focused

```python
# ✅ Good - single responsibility
def export_data():
    return generate_pdf()

# ❌ Bad - does too much
def export_data():
    # saves, validates, exports, sends email, logs...
```

### 3. Custom Success Messages

```python
# ✅ Include relevant metrics
success_message="✅ 5 documents exported in 2.3s"

# ❌ Generic
success_message="Done"
```

### 4. Progress Threshold Tuning

```python
# Fast app (should feel snappy)
progress_threshold=0.5  # Show progress after 0.5s

# Normal app (default)
progress_threshold=2.0  # Show progress after 2s

# Heavy operations
progress_threshold=5.0  # Show progress after 5s
```

### 5. Conditional Rendering

```python
# Show/hide based on state
if user_logged_in:
    if professional_button("action_btn", ...):
        pass

# Disable based on condition
if not required_field:
    st.info("Fill in field to proceed")
    # Return early or set button disabled via condition
```

## 🎪 Demo & Examples

See interactive examples:

```bash
streamlit run pages/06_Button_Examples.py
```

This page demonstrates:
- Quick actions (no progress bar)
- Long-running tasks (progress bar visible)
- Buttons with parameters
- Multiple independent buttons
- Conditional buttons
- Error handling

## 🐛 Troubleshooting

### Button stays disabled after error

**Problem**: Task throws exception, button remains disabled

**Solution**: Your `on_click` should handle errors gracefully

```python
def my_task():
    try:
        # your logic
        return result
    except Exception as e:
        st.error(f"Failed: {e}")
        return None
```

### Success message doesn't show

**Problem**: Task completes but no success toast

**Solution**: Check that `on_click` doesn't crash silently

```python
def my_task():
    # Make sure it returns normally
    return result  # Add this
```

### Multiple buttons conflicting

**Problem**: Clicking one button affects another

**Solution**: Ensure unique `button_id` for each button

```python
# ✅ Each unique
professional_button("export_btn", ..., on_click=export)
professional_button("delete_btn", ..., on_click=delete)

# ❌ Both use same ID - will conflict!
professional_button("btn", ..., on_click=export)
professional_button("btn", ..., on_click=delete)
```

### Progress bar never shows

**Problem**: Task takes 3+ seconds but no progress bar

**Solution**: Lower the threshold or verify task duration

```python
# Change to:
progress_threshold=1.0  # Instead of 2.0

# Or verify task really takes that long
import time
start = time.time()
# ... task ...
print(f"Took {time.time() - start:.1f}s")
```

## 📊 Performance

- **No external dependencies** beyond Streamlit
- **Minimal session state footprint** (~3 keys per button)
- **Non-blocking** - uses threading for progress monitoring
- **Memory efficient** - cleans up state after execution

## 🔐 Security

- No credentials stored
- No external calls required  
- All execution happens in your function
- Task isolation via session state

## 📝 License & Attribution

Part of RequirementsIQ project. Free to use and modify.

## 🤝 Contributing

Found an issue or have an improvement? 

Check the code in:
- `utils/professional_button.py` - Main implementation
- `pages/06_Button_Examples.py` - Demo and test cases

## 📖 Additional Resources

- [Streamlit Button Docs](https://docs.streamlit.io/library/api-reference/widgets/st.button)
- [Session State Guide](https://docs.streamlit.io/library/api-reference/session-state)
- [PROFESSIONAL_BUTTON_GUIDE.md](PROFESSIONAL_BUTTON_GUIDE.md) - Complete reference
- [INTEGRATION_EXAMPLE_Generate.py](INTEGRATION_EXAMPLE_Generate.py) - Real-world usage

---

**Version**: 1.0  
**Last Updated**: 2026-02-22  
**Status**: Production Ready ✅
