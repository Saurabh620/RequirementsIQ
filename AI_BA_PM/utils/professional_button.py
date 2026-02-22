"""
Professional SaaS Button Behavior Manager
Handles: disable state, spinner, progress bar, success toast, execution time, confirmation animation
Uses session_state to prevent duplicate clicks and manage UI state
"""
import time
import streamlit as st
from typing import Callable, Any, Optional, Dict


class ProfessionalButton:
    """
    Manager for professional SaaS-style button behavior.
    
    Features:
    - Prevents duplicate clicks via session_state
    - Auto-disables button during task execution
    - Shows spinner immediately
    - Shows progress bar if task takes >2 seconds
    - Displays success toast with execution time
    - Subtle confirmation animation
    - Clean, minimal UI
    """

    def __init__(self, button_id: str, label: str = "Execute"):
        """
        Initialize button manager.
        
        Args:
            button_id: Unique identifier for this button (used in session_state)
            label: Button label text
        """
        self.button_id = button_id
        self.label = label
        self.is_processing = False
        self._init_session_state()

    def _init_session_state(self):
        """Initialize session state keys for this button."""
        key_processing = f"_pb_processing_{self.button_id}"
        key_start_time = f"_pb_start_{self.button_id}"
        key_exec_time = f"_pb_exec_time_{self.button_id}"

        if key_processing not in st.session_state:
            st.session_state[key_processing] = False
        if key_start_time not in st.session_state:
            st.session_state[key_start_time] = None
        if key_exec_time not in st.session_state:
            st.session_state[key_exec_time] = None

    def _get_processing_state(self) -> bool:
        """Check if button is currently processing."""
        return st.session_state.get(f"_pb_processing_{self.button_id}", False)

    def _set_processing_state(self, state: bool):
        """Set processing state."""
        st.session_state[f"_pb_processing_{self.button_id}"] = state

    def _set_start_time(self, ts: Optional[float] = None):
        """Record start time."""
        st.session_state[f"_pb_start_{self.button_id}"] = ts

    def _get_start_time(self) -> Optional[float]:
        """Get start time."""
        return st.session_state.get(f"_pb_start_{self.button_id}")

    def _set_exec_time(self, seconds: float):
        """Record execution time."""
        st.session_state[f"_pb_exec_time_{self.button_id}"] = seconds

    def _get_exec_time(self) -> Optional[float]:
        """Get execution time."""
        return st.session_state.get(f"_pb_exec_time_{self.button_id}")

    def render(
        self,
        on_click: Callable[..., Any],
        *on_click_args,
        button_type: str = "primary",
        use_container_width: bool = True,
        icon: str = "⚡",
        show_progress_bar: bool = True,
        progress_threshold: float = 2.0,
        success_message: Optional[str] = None,
        **on_click_kwargs,
    ) -> bool:
        """
        Render and manage professional button with SaaS behavior.

        Args:
            on_click: Callback function to execute when button is clicked
            *on_click_args: Positional arguments for on_click
            button_type: "primary", "secondary", "tertiary"
            use_container_width: Whether button spans full width
            icon: Icon to show in button (e.g., "⚡", "🚀", "✨")
            show_progress_bar: Whether to show progress bar (>2 sec)
            progress_threshold: Seconds before showing progress bar
            success_message: Custom success message (if None, shows exec time)
            **on_click_kwargs: Keyword arguments for on_click

        Returns:
            bool: True if button was clicked and execution completed
        """
        is_processing = self._get_processing_state()

        # ── Render button (disabled if processing) ──────────────────────
        button_clicked = st.button(
            label=self.label,
            key=f"{self.button_id}_btn",
            type=button_type,
            use_container_width=use_container_width,
            disabled=is_processing,
            on_click=lambda: self._set_processing_state(True),
        )

        # ── No click yet, or already processed ──────────────────────────
        if not button_clicked:
            # Show success message from previous execution if exists
            exec_time = self._get_exec_time()
            if exec_time is not None and exec_time > 0:
                msg = success_message or f"✅ Completed in {exec_time:.1f}s"
                st.success(msg, icon="✅")
                # Clear after showing once
                self._set_exec_time(None)
            return False

        # ── Button just clicked: Execute task ──────────────────────────
        if is_processing:
            self._execute_task(
                on_click=on_click,
                on_click_args=on_click_args,
                on_click_kwargs=on_click_kwargs,
                show_progress_bar=show_progress_bar,
                progress_threshold=progress_threshold,
                success_message=success_message,
            )
            return True

        return False

    def _execute_task(
        self,
        on_click: Callable,
        on_click_args: tuple,
        on_click_kwargs: dict,
        show_progress_bar: bool,
        progress_threshold: float,
        success_message: Optional[str],
    ):
        """Execute the task with visual feedback."""
        start_time = time.time()
        self._set_start_time(start_time)

        # ── Show spinner immediately ──────────────────────────────────
        spinner_container = st.empty()
        progress_container = st.empty()
        status_container = st.empty()

        def update_status(message: str):
            """Update status message."""
            status_container.markdown(f"**{message}**")

        try:
            # Show initial spinner
            with spinner_container.container():
                with st.spinner("🔄 Processing..."):
                    start_exec = time.time()

                    # Check if we should show progress bar
                    if show_progress_bar:
                        # Run task while monitoring time
                        result = self._execute_with_progress_monitor(
                            on_click=on_click,
                            on_click_args=on_click_args,
                            on_click_kwargs=on_click_kwargs,
                            progress_container=progress_container,
                            progress_threshold=progress_threshold,
                            status_callback=update_status,
                        )
                    else:
                        # Just run the task
                        result = on_click(*on_click_args, **on_click_kwargs)

                    exec_time = time.time() - start_exec

            # ── Clear temporary containers ─────────────────────────────
            spinner_container.empty()
            progress_container.empty()
            status_container.empty()

            # ── Subtle confirmation animation ──────────────────────────
            # Quick success flash
            with st.container():
                st.markdown(
                    """
                    <div style="animation: slideIn 0.3s ease-out; color: #34d399; font-weight: 600;">
                    ✅ Success
                    </div>
                    <style>
                    @keyframes slideIn {
                        from { opacity: 0; transform: translateY(-10px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

            # ── Store execution time and show success toast ────────────
            self._set_exec_time(exec_time)
            msg = success_message or f"✅ Completed in {exec_time:.1f}s"
            st.success(msg, icon="✅")

            # Reset state for next run
            self._set_processing_state(False)

            return result

        except Exception as e:
            # ── Handle errors gracefully ──────────────────────────────
            spinner_container.empty()
            progress_container.empty()
            status_container.empty()

            exec_time = time.time() - start_time
            self._set_processing_state(False)

            st.error(f"❌ Failed after {exec_time:.1f}s: {str(e)}", icon="❌")
            raise

    def _execute_with_progress_monitor(
        self,
        on_click: Callable,
        on_click_args: tuple,
        on_click_kwargs: dict,
        progress_container,
        progress_threshold: float,
        status_callback: Callable[[str], None],
    ) -> Any:
        """
        Execute task and show progress bar if it takes longer than threshold.
        """
        import threading

        result = None
        exception = None
        start_time = time.time()
        progress_shown = False

        def run_task():
            nonlocal result, exception
            try:
                result = on_click(*on_click_args, **on_click_kwargs)
            except Exception as e:
                exception = e

        # Start task in thread to monitor time
        task_thread = threading.Thread(target=run_task, daemon=True)
        task_thread.start()

        # Monitor progress
        while task_thread.is_alive():
            elapsed = time.time() - start_time

            # Show progress bar after threshold
            if elapsed > progress_threshold and not progress_shown:
                progress_shown = True
                status_callback(f"⏱️ Processing... ({elapsed:.1f}s)")

            if progress_shown:
                # Update progress indication (simple pulsing effect)
                progress_pct = min(0.9, elapsed / (progress_threshold * 3))
                with progress_container.container():
                    st.progress(progress_pct, text=f"⏳ {elapsed:.1f}s elapsed")

            time.sleep(0.2)

        # Wait for thread to finish
        task_thread.join()

        # Clear progress
        progress_container.empty()
        status_callback("")

        if exception:
            raise exception

        return result


def professional_button(
    button_id: str,
    label: str,
    on_click: Callable[..., Any],
    *on_click_args,
    button_type: str = "primary",
    use_container_width: bool = True,
    icon: str = "⚡",
    show_progress_bar: bool = True,
    progress_threshold: float = 2.0,
    success_message: Optional[str] = None,
    **on_click_kwargs,
) -> bool:
    """
    Convenience function for rendering a professional button.

    Args:
        button_id: Unique identifier for button state management
        label: Button display text
        on_click: Function to execute on click
        *on_click_args: Positional args for on_click
        button_type: "primary" | "secondary" | "tertiary"
        use_container_width: Span full width
        icon: Icon emoji (unused in current version, for future use)
        show_progress_bar: Show progress for long tasks
        progress_threshold: Seconds before showing progress
        success_message: Custom success message
        **on_click_kwargs: Keyword args for on_click

    Returns:
        bool: True if task completed successfully

    Example:
        >>> def my_task():
        >>>     time.sleep(3)
        >>>     return "done"
        >>> 
        >>> if professional_button(
        >>>     button_id="generate_btn",
        >>>     label="⚡ Generate Documents",
        >>>     on_click=my_task,
        >>>     success_message="Documents ready to download!"
        >>> ):
        >>>     st.info("Task completed!")
    """
    pb = ProfessionalButton(button_id, label)
    return pb.render(
        on_click=on_click,
        *on_click_args,
        button_type=button_type,
        use_container_width=use_container_width,
        icon=icon,
        show_progress_bar=show_progress_bar,
        progress_threshold=progress_threshold,
        success_message=success_message,
        **on_click_kwargs,
    )
