import hashlib
import hmac
import re
import secrets
import time
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

CSRF_PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

_API_PREFIX = re.compile(r"^/api/v\d+/")

_EXEMPT_PATHS = {
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/logout",
    "/api/v1/auth/logout-all",
    "/api/v1/payments/webhook/yookassa",
    "/api/v1/telegram/webhook",
}

CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_TOKEN_EXPIRY = 3600  # 1 hour


def _get_csrf_secret() -> bytes:
    """Get or generate CSRF secret key."""
    secret = getattr(settings, "CSRF_SECRET_KEY", settings.APP_SECRET_KEY)
    return secret.encode("utf-8") if isinstance(secret, str) else secret


def generate_csrf_token(session_id: str | None = None) -> str:
    """Generate a cryptographically secure CSRF token using real random tokens."""
    timestamp = int(time.time())
    # Используем secrets.token_hex для генерации настоящего случайного токена
    random_bytes = secrets.token_hex(32)
    
    if session_id:
        message = f"{session_id}:{timestamp}:{random_bytes}"
    else:
        message = f"{timestamp}:{random_bytes}"
    
    signature = hmac.new(
        _get_csrf_secret(),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    return f"{timestamp}:{random_bytes}:{signature}"


def validate_csrf_token(token: str, session_id: str | None = None) -> bool:
    """Validate CSRF token."""
    if not token:
        return False
    
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return False
        
        timestamp_str, random_bytes, signature = parts
        timestamp = int(timestamp_str)
        
        # Check expiry
        now = int(time.time())
        if now - timestamp > CSRF_TOKEN_EXPIRY:
            return False
        
        # Verify signature
        if session_id:
            expected_message = f"{session_id}:{timestamp}:{random_bytes}"
        else:
            expected_message = f"{timestamp}:{random_bytes}"
        
        expected_signature = hmac.new(
            _get_csrf_secret(),
            expected_message.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    except (ValueError, TypeError):
        return False


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        method = request.method
        
        # Generate CSRF token for GET requests and set cookie
        if method == "GET" and _API_PREFIX.match(path):
            response = await call_next(request)
            
            # Generate new token if not present or expired
            existing_token = request.cookies.get(CSRF_COOKIE_NAME)
            if not existing_token or not validate_csrf_token(existing_token):
                new_token = generate_csrf_token()
                response.set_cookie(
                    CSRF_COOKIE_NAME,
                    new_token,
                    max_age=CSRF_TOKEN_EXPIRY,
                    httponly=False,  # Must be accessible to JavaScript
                    samesite="lax",
                    secure=settings.APP_ENV == "production",
                    path="/",
                )
            
            return response
        
        # Validate CSRF for state-changing methods
        if method in CSRF_PROTECTED_METHODS:
            if _API_PREFIX.match(path) and path not in _EXEMPT_PATHS:
                # Double-submit cookie pattern: compare cookie token with header token
                cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
                header_token = request.headers.get(CSRF_HEADER_NAME)
                
                # Also support X-Requested-With for backward compatibility
                requested_with = request.headers.get("X-Requested-With")
                
                if not cookie_token and not header_token and not requested_with:
                    return Response(
                        status_code=403,
                        content='{"detail": "CSRF: missing CSRF token. Use double-submit cookie pattern or X-Requested-With header."}',
                        media_type="application/json",
                    )
                
                # If both tokens provided, they must match
                if cookie_token and header_token:
                    if not hmac.compare_digest(cookie_token, header_token):
                        return Response(
                            status_code=403,
                            content='{"detail": "CSRF: token mismatch"}',
                            media_type="application/json",
                        )
                elif header_token and not cookie_token:
                    # Header-only mode (for API clients)
                    pass
                elif cookie_token and not header_token:
                    # Cookie-only is not sufficient for state-changing requests
                    if not requested_with:
                        return Response(
                            status_code=403,
                            content='{"detail": "CSRF: missing X-CSRF-Token header"}',
                            media_type="application/json",
                        )
        
        return await call_next(request)
