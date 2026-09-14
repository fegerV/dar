import logging
import time
from collections import defaultdict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger(__name__)

RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 120
RATE_LIMIT_PREFIX = "daragent:ratelimit:"

LOGIN_WINDOW = 300
LOGIN_MAX = 10
LOGIN_PREFIX = "daragent:login:"

_rate_store: dict[str, list[float]] = defaultdict(list)
_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        try:
            import redis.asyncio as redis

            if settings.REDIS_RATE_LIMIT_URL:
                _redis_client = redis.from_url(settings.REDIS_RATE_LIMIT_URL, decode_responses=True)
        except Exception as exc:
            logger.warning("Rate limit: Redis client unavailable, using in-memory store: %s", exc)
            _redis_client = None
    return _redis_client


def _memory_hit(key: str, window_seconds: int, limit: int, now: float) -> bool:
    """In-memory sliding window. Returns True when the limit is exceeded."""
    window = [t for t in _rate_store[key] if now - t < window_seconds]
    if len(window) >= limit:
        _rate_store[key] = window
        return True
    window.append(now)
    _rate_store[key] = window
    return False


async def _hit(key: str, window_seconds: int, limit: int, now: float) -> bool:
    """Register one hit and report whether the caller is over the limit.

    Redis holds the counter shared across worker processes. If Redis is
    unreachable we fall back to the in-process store rather than swallowing the
    error — silently skipping the increment would disable rate limiting
    entirely and leave login brute-force protection off.
    """
    redis_client = _get_redis()
    if redis_client is not None:
        try:
            current = await redis_client.get(key)
            count = int(current) if current else 0
            if count >= limit:
                return True
            pipe = redis_client.pipeline()
            pipe.incr(key)
            if count == 0:
                pipe.expire(key, window_seconds)
            await pipe.execute()
            return False
        except Exception as exc:
            logger.warning("Rate limit: Redis error, falling back to in-memory store: %s", exc)
    return _memory_hit(key, window_seconds, limit, now)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else "anonymous"
        now = time.time()

        # Stricter limit for login attempts (brute-force protection).
        if request.url.path == "/api/v1/auth/login" and request.method == "POST":
            if await _hit(f"{LOGIN_PREFIX}{client}", LOGIN_WINDOW, LOGIN_MAX, now):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many login attempts. Please try again later."},
                )

        key = f"{RATE_LIMIT_PREFIX}{client}:{request.url.path}"
        if await _hit(key, RATE_LIMIT_WINDOW, RATE_LIMIT_MAX, now):
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

        return await call_next(request)
