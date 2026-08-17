import time
from collections import defaultdict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 120

_rate_store: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else "anonymous"
        key = f"{client}:{request.url.path}"
        now = time.time()
        window = [t for t in _rate_store[key] if now - t < RATE_LIMIT_WINDOW]
        _rate_store[key] = window
        if len(window) >= RATE_LIMIT_MAX:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        _rate_store[key].append(now)
        return await call_next(request)
