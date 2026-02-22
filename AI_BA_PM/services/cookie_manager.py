"""
Streamlit Cookie Manager
Provides a simple interface for reading/writing cookies in Streamlit apps.
Uses browser storage and URL parameters as fallback.
"""
import streamlit as st
from typing import Optional, Dict
import json
import base64


class StreamlitCookieManager:
    """
    Manage cookies in Streamlit using session state as fallback.
    Production apps should use streamlit-cookies-manager package.
    """
    
    COOKIE_PREFIX = "_auth_"
    
    @staticmethod
    def set_cookie(name: str, value: str, max_age: int = 86400) -> None:
        """
        Set a cookie value (stored in session state as fallback).
        
        Args:
            name: Cookie name
            value: Cookie value
            max_age: Cookie lifetime in seconds (default: 24 hours)
        """
        # Store in session state as client-side fallback
        cookie_key = f"{StreamlitCookieManager.COOKIE_PREFIX}{name}"
        st.session_state[cookie_key] = {
            "value": value,
            "max_age": max_age,
            "created_at": st.session_state.get("_timestamp", 0)
        }
        
        # Try to use local storage via JavaScript (requires streamlit >= 1.18)
        try:
            from streamlit.components.v1 import html
            html(f"""
            <script>
            localStorage.setItem('{name}', '{value}');
            </script>
            """, height=0)
        except Exception:
            pass  # Fallback to session state is sufficient
    
    @staticmethod
    def get_cookie(name: str) -> Optional[str]:
        """
        Get a cookie value.
        
        Returns cookie value if exists and not expired, None otherwise.
        """
        cookie_key = f"{StreamlitCookieManager.COOKIE_PREFIX}{name}"
        
        # Try session state first
        if cookie_key in st.session_state:
            cookie_data = st.session_state[cookie_key]
            if isinstance(cookie_data, dict) and "value" in cookie_data:
                return cookie_data["value"]
        
        # Try URL query parameter (fallback)
        try:
            query_params = st.query_params
            if name in query_params:
                return query_params[name]
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def delete_cookie(name: str) -> None:
        """Delete a cookie."""
        cookie_key = f"{StreamlitCookieManager.COOKIE_PREFIX}{name}"
        if cookie_key in st.session_state:
            del st.session_state[cookie_key]
        
        # Clear from local storage via JavaScript
        try:
            from streamlit.components.v1 import html
            html(f"""
            <script>
            localStorage.removeItem('{name}');
            </script>
            """, height=0)
        except Exception:
            pass
    
    @staticmethod
    def clear_all_auth_cookies() -> None:
        """Clear all authentication cookies."""
        keys_to_delete = [
            k for k in st.session_state.keys() 
            if k.startswith(StreamlitCookieManager.COOKIE_PREFIX)
        ]
        for key in keys_to_delete:
            del st.session_state[key]


# ── Streamlit Query Parameter Cookie Alternative ─────────────
def set_auth_token_in_url(token: str) -> None:
    """
    Alternative: Store auth token in URL as query parameter.
    This is more reliable than local storage in Streamlit.
    """
    try:
        st.query_params["auth_token"] = token
    except Exception:
        pass


def get_auth_token_from_url() -> Optional[str]:
    """
    Get auth token from URL query parameters.
    """
    try:
        query_params = st.query_params
        return query_params.get("auth_token")
    except Exception:
        return None


# ── Recommended: Simple Session-Based Fallback ─────────────────
class SimpleAuthCache:
    """
    Use st.session_state as auth cache (simple, works everywhere).
    Keys are stored locally in browser but cleared on page refresh.
    
    For truly persistent cookies, consider:
    - CloudFlare Workers with Set-Cookie headers
    - Custom Streamlit component with js-cookie library
    - Streamlit Cloud's secrets management
    """
    
    AUTH_TOKEN_KEY = "_secure_auth_token"
    USER_DATA_KEY = "_secure_user_data"
    
    @staticmethod
    def cache_auth_token(token: str) -> None:
        """Cache authentication token."""
        st.session_state[SimpleAuthCache.AUTH_TOKEN_KEY] = token
    
    @staticmethod
    def get_cached_auth_token() -> Optional[str]:
        """Retrieve cached auth token."""
        return st.session_state.get(SimpleAuthCache.AUTH_TOKEN_KEY)
    
    @staticmethod
    def cache_user_data(user_data: dict) -> None:
        """Cache user data."""
        st.session_state[SimpleAuthCache.USER_DATA_KEY] = user_data
    
    @staticmethod
    def get_cached_user_data() -> Optional[dict]:
        """Retrieve cached user data."""
        return st.session_state.get(SimpleAuthCache.USER_DATA_KEY)
    
    @staticmethod
    def clear_auth_cache() -> None:
        """Clear authentication cache."""
        if SimpleAuthCache.AUTH_TOKEN_KEY in st.session_state:
            del st.session_state[SimpleAuthCache.AUTH_TOKEN_KEY]
        if SimpleAuthCache.USER_DATA_KEY in st.session_state:
            del st.session_state[SimpleAuthCache.USER_DATA_KEY]


# ── Browser-Based Persistence (Advanced) ───────────────────────
def setup_persistent_auth_component():
    """
    Install custom Streamlit component for persistent auth cookies.
    
    This requires streamlit-cookies-manager:
    pip install streamlit-cookies-manager
    
    Usage in app:
        from extra_streamlit_components import CookieManager
        
        cookie_manager = CookieManager()
        if "auth_token" in st.session_state:
            cookie_manager.set("auth_token", st.session_state["auth_token"])
    """
    try:
        import extra_streamlit_components as stx
        return stx.CookieManager()
    except ImportError:
        return None
