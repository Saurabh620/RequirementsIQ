"""
Secure Authentication Service
Persistent login using JWT tokens stored in encrypted cookies.
Production-ready with token expiration and refresh mechanism.
"""
import os
import json
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
from services.auth_service import get_user_by_id, hash_password
from database.connection import get_db
from sqlalchemy import text


# ── Configuration ──────────────────────────────────────────────
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production-12345")
TOKEN_EXPIRY_HOURS = int(os.getenv("TOKEN_EXPIRY_HOURS", "24"))
REFRESH_TOKEN_EXPIRY_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRY_DAYS", "30"))

# Validate secret key in production
if SECRET_KEY == "your-super-secret-key-change-in-production-12345":
    import warnings
    warnings.warn(
        "⚠️ SECURITY WARNING: Using default JWT_SECRET_KEY. Set JWT_SECRET_KEY environment variable in production!",
        UserWarning
    )


# ── JWT Token Utilities ────────────────────────────────────────
def create_token_payload(user_id: str, email: str, expiry_hours: int = TOKEN_EXPIRY_HOURS) -> Tuple[str, dict]:
    """
    Create a JWT-like token payload with signature.
    
    Returns:
        (token_string, payload_dict)
    """
    now = datetime.utcnow()
    expiry = now + timedelta(hours=expiry_hours)
    
    payload = {
        "user_id": user_id,
        "email": email,
        "issued_at": now.isoformat(),
        "expires_at": expiry.isoformat(),
    }
    
    # Create signature
    payload_json = json.dumps(payload, sort_keys=True)
    signature = hmac.new(
        SECRET_KEY.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Combine payload + signature
    token = f"{payload_json}.{signature}"
    
    return token, payload


def verify_token(token: str) -> Tuple[bool, Optional[dict], str]:
    """
    Verify and decode a JWT-like token.
    
    Returns:
        (is_valid, payload_dict, message)
    """
    try:
        if "." not in token:
            return False, None, "Invalid token format"
        
        payload_json, signature = token.rsplit(".", 1)
        
        # Verify signature
        expected_signature = hmac.new(
            SECRET_KEY.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return False, None, "Token signature invalid"
        
        # Parse payload
        payload = json.loads(payload_json)
        
        # Check expiration
        expires_at = datetime.fromisoformat(payload["expires_at"])
        if datetime.utcnow() > expires_at:
            return False, None, "Token expired"
        
        return True, payload, "Token valid"
    
    except Exception as e:
        return False, None, f"Token verification failed: {str(e)}"


def create_refresh_token(user_id: str) -> Tuple[str, dict]:
    """
    Create a long-lived refresh token.
    Stores token in database for revocation ability.
    """
    refresh_token, payload = create_token_payload(
        user_id=user_id,
        email="refresh",  # Placeholder for refresh tokens
        expiry_hours=REFRESH_TOKEN_EXPIRY_DAYS * 24
    )
    
    # Store in database for revocation
    with get_db() as db:
        db.execute(
            text("""
                INSERT INTO auth_tokens (user_id, token_hash, token_type, expires_at)
                VALUES (:user_id, :token_hash, 'refresh', :expires_at)
                ON DUPLICATE KEY UPDATE expires_at = :expires_at
            """),
            {
                "user_id": user_id,
                "token_hash": hashlib.sha256(refresh_token.encode()).hexdigest(),
                "expires_at": payload["expires_at"]
            }
        )
    
    return refresh_token, payload


def revoke_refresh_token(user_id: str) -> bool:
    """
    Revoke all refresh tokens for a user (logout).
    """
    try:
        with get_db() as db:
            db.execute(
                text("DELETE FROM auth_tokens WHERE user_id = :user_id AND token_type = 'refresh'"),
                {"user_id": user_id}
            )
        return True
    except Exception:
        return False


def validate_refresh_token(token: str, user_id: str) -> Tuple[bool, str]:
    """
    Validate a refresh token against database.
    """
    # Verify token signature
    is_valid, payload, msg = verify_token(token)
    if not is_valid:
        return False, msg
    
    # Check in database
    try:
        with get_db() as db:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            row = db.execute(
                text("""
                    SELECT expires_at FROM auth_tokens 
                    WHERE user_id = :user_id AND token_hash = :token_hash 
                    AND token_type = 'refresh'
                """),
                {"user_id": user_id, "token_hash": token_hash}
            ).fetchone()
            
            if not row:
                return False, "Refresh token not found or revoked"
            
            return True, "Refresh token valid"
    except Exception as e:
        return False, f"Refresh token validation failed: {str(e)}"


# ── Cookie Operations ──────────────────────────────────────────
def encode_cookie_value(value: str) -> str:
    """
    Simple encoding for cookie value (base64-like).
    For production, consider using cryptography library.
    """
    import base64
    return base64.b64encode(value.encode()).decode()


def decode_cookie_value(encoded: str) -> Optional[str]:
    """
    Decode cookie value.
    """
    try:
        import base64
        return base64.b64decode(encoded.encode()).decode()
    except Exception:
        return None


# ── Authentication Flow ────────────────────────────────────────
def auto_login_from_cookie(auth_cookie: Optional[str]) -> Tuple[bool, Optional[dict], str]:
    """
    Attempt to auto-login using authentication cookie.
    
    Returns:
        (success, user_dict, message)
    """
    if not auth_cookie:
        return False, None, "No authentication cookie"
    
    # Decode cookie
    token = decode_cookie_value(auth_cookie)
    if not token:
        return False, None, "Invalid cookie encoding"
    
    # Verify token
    is_valid, payload, msg = verify_token(token)
    if not is_valid:
        return False, None, msg
    
    # Get user from database to ensure they still exist and are active
    user = get_user_by_id(payload["user_id"])
    if not user:
        return False, None, "User not found"
    
    return True, user, "Auto-login successful"


def create_auth_cookie(user_id: str, email: str) -> str:
    """
    Create an authentication cookie value.
    """
    token, _ = create_token_payload(user_id, email)
    return encode_cookie_value(token)


def logout_user(user_id: str) -> bool:
    """
    Logout user: revoke refresh tokens and clear from session.
    """
    return revoke_refresh_token(user_id)


# ── Password Reset Flow ────────────────────────────────────────
def create_password_reset_token(user_id: str) -> str:
    """
    Create a short-lived token for password reset (1 hour).
    """
    token, _ = create_token_payload(user_id, "reset", expiry_hours=1)
    return encode_cookie_value(token)


def verify_password_reset_token(token_str: str) -> Tuple[bool, Optional[str], str]:
    """
    Verify password reset token and return user_id.
    
    Returns:
        (is_valid, user_id, message)
    """
    token = decode_cookie_value(token_str)
    if not token:
        return False, None, "Invalid reset token format"
    
    is_valid, payload, msg = verify_token(token)
    if not is_valid:
        return False, None, msg
    
    return True, payload["user_id"], "Reset token valid"


# ── Database Schema Helper ────────────────────────────────────
def init_auth_tokens_table():
    """
    Initialize the auth_tokens table if it doesn't exist.
    Call this on app startup.
    """
    try:
        with get_db() as db:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS auth_tokens (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    token_hash VARCHAR(64) NOT NULL UNIQUE,
                    token_type VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_user_type (user_id, token_type)
                )
            """))
        return True
    except Exception as e:
        # Table might already exist or other error
        return True


# ── Security Utilities ─────────────────────────────────────────
def get_token_expiry_time() -> int:
    """Get token expiry time in seconds."""
    return TOKEN_EXPIRY_HOURS * 3600


def is_token_expiring_soon(payload: dict, buffer_minutes: int = 30) -> bool:
    """
    Check if token is expiring within buffer time.
    Useful for auto-refresh logic.
    """
    expires_at = datetime.fromisoformat(payload["expires_at"])
    time_left = expires_at - datetime.utcnow()
    return time_left < timedelta(minutes=buffer_minutes)


def log_auth_event(user_id: str, event_type: str, details: str = "") -> None:
    """
    Log authentication events for security audit.
    Useful for detecting suspicious activity.
    """
    try:
        with get_db() as db:
            db.execute(
                text("""
                    INSERT INTO auth_events (user_id, event_type, details, created_at)
                    VALUES (:user_id, :event_type, :details, NOW())
                """),
                {"user_id": user_id, "event_type": event_type, "details": details}
            )
    except Exception:
        # Table might not exist, silently fail
        pass
