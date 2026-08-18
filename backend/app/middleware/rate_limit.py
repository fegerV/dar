import time
from collections import defaultdict

import redis.asyncio as redis
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings

RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 120
RATE_LIMIT_PREFIX = "daragent:ratelimit:"

_rate_store: dict[str, list[float]] = defaultdict(list)
_redis_client: redis.Redis | None = None


def _get_redis() -> redis.Redis | None:
    global _redis_client
    if _redis_client is None and settings.REDIS_RATE_LIMIT_URL:
        try:
            _redis_client = redis.from_url(settings.REDIS_RATE_LIMIT_URL, decode_responses=True)
        except Exception:
            _redis_client = None
    return _redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
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
