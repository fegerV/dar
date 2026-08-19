import time
from collections import defaultdict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings

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
        except Exception:
            _redis_client = None
    return _redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if (
            request.url.path == "/api/v1/auth/login"
            and request.method == "POST"
        ):
            client = request.client.host if request.client else "anonymous"
            login_key = f"{LOGIN_PREFIX}{client}"
            now = time.time()
            redis_client = _get_redis()
            try:
                if redis_client:
                    current = await redis_client.get(login_key)
                    count = int(current) if current else 0
                    if count >= LOGIN_MAX:
                        return JSONResponse(
                            status_code=429,
                            content={"detail": "Too many login attempts. Please try again later."},
                        )
                    pipe = redis_client.pipeline()
                    pipe.incr(login_key)
                    if count == 0:
                        pipe.expire(login_key, LOGIN_WINDOW)
                    await pipe.execute()
                else:
                    window = [t for t in _rate_store[login_key] if now - t < LOGIN_WINDOW]
                    _rate_store[login_key] = window
                    if len(window) >= LOGIN_MAX:
                        return JSONResponse(
                            status_code=429,
                            content={"detail": "Too many login attempts. Please try again later."},
                        )
                    _rate_store[login_key].append(now)
            except Exception:
                pass

        client = request.client.host if request.client else "anonymous"
        key = f"{RATE_LIMIT_PREFIX}{client}:{request.url.path}"
        now = time.time()
        redis_client = _get_redis()

        if redis_client:
            try:
                current = await redis_client.get(key)
                count = int(current) if current else 0
                if count >= RATE_LIMIT_MAX:
                    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
                pipe = redis_client.pipeline()
                pipe.incr(key)
                if count == 0:
                    pipe.expire(key, RATE_LIMIT_WINDOW)
                await pipe.execute()
            except Exception:
                pass
        else:
            window = [t for t in _rate_store[key] if now - t < RATE_LIMIT_WINDOW]
            _rate_store[key] = window
            if len(window) >= RATE_LIMIT_MAX:
                return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
            _rate_store[key].append(now)

        return await call_next(request)
