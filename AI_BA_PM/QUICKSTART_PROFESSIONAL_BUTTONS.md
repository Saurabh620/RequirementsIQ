# ⚡ 5-Minute Quick Start

Get professional buttons in your app in 5 minutes.

## Step 1: Add Import (30 seconds)

In your page (e.g., `pages/01_Generate.py`):

```python
from utils.professional_button import professional_button
```

## Step 2: Extract Task Function (1 minute)

Wrap your task in a function:

```python
def execute_generation_pipeline():
    """Your existing logic here"""
    doc_id = save_document(...)
    result = run_pipeline(...)
    return doc_id
```

## Step 3: Replace Button (2 minutes)

**BEFORE:**
```python
if st.button("⚡ Generate Documents", type="primary", 
             use_container_width=True, disabled=not raw_text):
    with st.spinner("Processing..."):
        # ... lots of code ...
    st.success("Done!")
```

**AFTER:**
```python
if professional_button(
    button_id="generate_documents_btn",
    label="⚡ Generate Documents",
    on_click=execute_generation_pipeline,
    button_type="primary",
    use_container_width=True,
    success_message=f"✅ Generated successfully!",
):
    st.info("Ready for next step")
```

## Step 4: Test (1.5 minutes)

Run your app:
```bash
streamlit run AI_BA_PM/app.py
```

Click the button and verify:
- ✅ Button disables
- ✅ Spinner shows
- ✅ Success message appears
- ✅ Shows execution time

## Step 5: Optional - Add CSS (30 seconds)

For professional animations, add to your page:

```python
from utils.professional_button_css import inject_professional_button_css
inject_professional_button_css()
```

---

**Done!** You now have professional SaaS button behavior.

## What You Get Automatically

| Feature | Before | After |
|---------|--------|-------|
| Duplicate click prevention | Manual | ✅ Automatic |
| Button disable | Manual | ✅ Automatic |
| Spinner | Manual | ✅ Automatic |
| Progress bar (>2sec) | ❌ No | ✅ Automatic |
| Success message | Manual | ✅ Automatic with time |
| Execution time | Manual | ✅ Automatic |

---

## For More Examples

See: `pages/06_Button_Examples.py`

Run: `streamlit run pages/06_Button_Examples.py`

---

## Common Use Cases

### Quick action (< 1 sec)
```python
if professional_button("action", "Click", fast_func): pass
```

### Long task (> 2 sec)
```python
if professional_button(
    "task", "Process", slow_func,
    progress_threshold=1.0,  # Show progress sooner
): pass
```

### With arguments
```python
if professional_button(
    "process", "Go", process_func,
    user_id, count=100,  # Pass args
): pass
```

### With custom message
```python
if professional_button(
    "export", "Export", export_func,
    success_message="✅ 50 docs exported in 2.3s"
): pass
```

---

## Troubleshooting

**Button stays disabled?**  
→ Make sure on_click function returns normally (doesn't crash)

**No progress bar?**  
→ Task must take > progress_threshold (default 2.0 seconds)

**Button not working?**  
→ Check button_id is unique, on_click is callable

---

That's it! You're done. Enjoy your professional buttons! 🎉
