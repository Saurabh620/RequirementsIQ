"""
Enhanced UI Theme with Professional Button CSS
Adds subtle animations and visual feedback for professional buttons.

Install this in your ui_theme.py or as a separate enhancement.
"""

PROFESSIONAL_BUTTON_CSS = """
<style>
/* ──────────────────────────────────────────────────────────────── */
/* Professional Button Animations */
/* ──────────────────────────────────────────────────────────────── */

/* Success toast animation - slides in from top */
@keyframes toast-slide-in {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Subtle pulse when button is disabled */
@keyframes button-disable-pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.7;
    }
}

/* Confirmation animation - checkmark fade in */
@keyframes confirmation-fadeIn {
    from {
        opacity: 0;
        transform: scale(0.8);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

/* Progress bar slide animation */
@keyframes progress-slide {
    from {
        transform: translateX(-100%);
    }
    to {
        transform: translateX(0);
    }
}

/* Spinner rotation */
@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

/* Apply animations to Streamlit elements */
div[data-testid="stAlertContainer"] {
    animation: toast-slide-in 0.3s ease-out;
}

/* Button disabled state (when processing) */
button[disabled] {
    animation: button-disable-pulse 1.5s ease-in-out infinite;
}

/* Success message styling */
div[data-testid="stAlert"] {
    animation: confirmation-fadeIn 0.3s ease-out;
    border-left: 4px solid #34d399 !important;
    background: rgba(52, 211, 153, 0.1) !important;
}

/* Progress bar styling */
div[class*="stProgress"] {
    animation: progress-slide 0.4s ease-out;
}

/* ──────────────────────────────────────────────────────────────── */
/* Professional Dashboard Button Styling */
/* ──────────────────────────────────────────────────────────────── */

/* Primary buttons - main action */
button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    transition: all 0.2s ease !important;
}

button[kind="primary"]:hover:not([disabled]) {
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4) !important;
    transform: translateY(-2px) !important;
}

button[kind="primary"]:active:not([disabled]) {
    transform: translateY(0) !important;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3) !important;
}

/* Secondary buttons - alternative actions */
button[kind="secondary"] {
    background: rgba(100, 116, 139, 0.1) !important;
    border: 1px solid rgba(148, 163, 184, 0.3) !important;
    color: #cbd5e1 !important;
    transition: all 0.2s ease !important;
}

button[kind="secondary"]:hover:not([disabled]) {
    background: rgba(100, 116, 139, 0.15) !important;
    border-color: rgba(148, 163, 184, 0.5) !important;
}

/* Disabled button state - during processing */
button[disabled] {
    opacity: 0.6 !important;
    cursor: not-allowed !important;
    background: rgba(100, 116, 139, 0.3) !important;
}

/* ──────────────────────────────────────────────────────────────── */
/* Status Indicators */
/* ──────────────────────────────────────────────────────────────── */

/* Success indicator */
.success-indicator {
    color: #34d399;
    font-weight: 600;
    animation: confirmation-fadeIn 0.3s ease-out;
}

/* Processing indicator */
.processing-indicator {
    display: inline-block;
    animation: spin 1s linear infinite;
}

/* Time elapsed indicator */
.time-elapsed {
    color: #94a3b8;
    font-size: 0.9rem;
    font-weight: 500;
}

/* ──────────────────────────────────────────────────────────────── */
/* Container Styling for Button Groups */
/* ──────────────────────────────────────────────────────────────── */

.button-container {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}

.button-container--vertical {
    flex-direction: column;
}

.button-container--center {
    justify-content: center;
}

.button-container--right {
    justify-content: flex-end;
}

/* ──────────────────────────────────────────────────────────────── */
/* Step Indicator Styling */
/* ──────────────────────────────────────────────────────────────── */

.step-label {
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #94a3b8;
    font-weight: 600;
    font-size: 0.85rem;
    margin-bottom: 1rem;
}

/* ──────────────────────────────────────────────────────────────── */
/* Toast/Alert Animations */
/* ──────────────────────────────────────────────────────────────── */

.toast-success {
    animation: toast-slide-in 0.3s ease-out;
    border-left: 4px solid #34d399;
}

.toast-error {
    animation: toast-slide-in 0.3s ease-out;
    border-left: 4px solid #f87171;
}

.toast-warning {
    animation: toast-slide-in 0.3s ease-out;
    border-left: 4px solid #fbbf24;
}

.toast-info {
    animation: toast-slide-in 0.3s ease-out;
    border-left: 4px solid #60a5fa;
}

/* ──────────────────────────────────────────────────────────────── */
/* Progress Bar Enhancement */
/* ──────────────────────────────────────────────────────────────── */

div[class*="stProgress"] > div {
    background: linear-gradient(
        90deg,
        #3b82f6 0%,
        #60a5fa 50%,
        #3b82f6 100%
    ) !important;
    background-size: 200% 100% !important;
    animation: progress-shine 2s ease-in-out infinite !important;
}

@keyframes progress-shine {
    0%, 100% {
        background-position: 200% 0;
    }
    50% {
        background-position: 0 0;
    }
}

/* ──────────────────────────────────────────────────────────────── */
/* Reduced Motion Support (Accessibility) */
/* ──────────────────────────────────────────────────────────────── */

@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
"""


def inject_professional_button_css():
    """
    Inject professional button CSS into your Streamlit app.
    
    Call this in your app.py or pages right after inject_theme():
    
    Example:
        from utils.ui_theme import inject_professional_button_css
        inject_professional_button_css()
    """
    import streamlit as st
    st.markdown(PROFESSIONAL_BUTTON_CSS, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# HOW TO USE IN YOUR APP
# ──────────────────────────────────────────────────────────────────────────────

"""
Option 1: Add to the top of app.py after other imports
(or any page that should have professional button styling)
====================================================

from utils.ui_theme import inject_theme, inject_professional_button_css

inject_theme()
inject_professional_button_css()


Option 2: Extend your existing ui_theme.py
==========================================

# In utils/ui_theme.py, add at the end:

PROFESSIONAL_BUTTON_CSS = '''[CSS from above]'''

def inject_professional_button_css():
    import streamlit as st
    st.markdown(PROFESSIONAL_BUTTON_CSS, unsafe_allow_html=True)

# Then call it in your pages:
from utils.ui_theme import inject_professional_button_css
inject_professional_button_css()
"""
