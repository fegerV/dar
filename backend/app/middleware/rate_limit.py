import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Literal

from fastapi import Request
from prometheus_client import Counter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.metrics import http_requests_total

logger = logging.getLogger(__name__)

# Rate limit metrics
rate_limit_exceeded_total = Counter(
    "daragent_rate_limit_exceeded_total",
    "Total rate limit exceeded events",
    ["endpoint_type", "client_id"],
)

# Sliding window log stores
_rate_store: dict[str, list[float]] = defaultdict(list)
_redis_client = None

# Endpoint-specific rate limits (sliding window)
@dataclass
class RateLimitConfig:
    window_seconds: int
    max_requests: int
    description: str

# Default global rate limit
DEFAULT_RATE_LIMIT = RateLimitConfig(window_seconds=60, max_requests=120, description="Global rate limit")

# Critical endpoint rate limits (stricter)
CRITICAL_ENDPOINTS = {
    "/api/v1/generations": RateLimitConfig(window_seconds=60, max_requests=10, description="Generation endpoint"),
    "/api/v1/payments": RateLimitConfig(window_seconds=60, max_requests=20, description="Payment endpoint"),
    "/api/v1/auth/login": RateLimitConfig(window_seconds=300, max_requests=10, description="Login endpoint"),
}

# Prefix for Redis keys
RATE_LIMIT_PREFIX = "daragent:ratelimit:"


def _get_redis():
    """Get or create Redis client."""
    global _redis_client
    if _redis_client is None:
        try:
            import redis.asyncio as redis

            if settings.REDIS_RATE_LIMIT_URL:
                _redis_client = redis.from_url(settings.REDIS_RATE_LIMIT_URL, decode_responses=True)
        except Exception as e:
            logger.warning("Failed to initialize Redis for rate limiting: %s", e)
            _redis_client = None
    return _redis_client


async def _check_rate_limit_sliding_window(
    key: str,
    config: RateLimitConfig,
    client_id: str,
    endpoint_type: str = "default",
) -> tuple[bool, int]:
    """
    Check rate limit using sliding window log algorithm.
    
    Returns:
        tuple: (allowed, remaining_requests)
    """
    now = time.time()
    window_start = now - config.window_seconds
    
    redis_client = _get_redis()
    
    if redis_client:
        try:
            # Use Redis sorted set for sliding window
            # Score = timestamp, Member = unique request ID
            pipe = redis_client.pipeline()
            
            # Remove old entries outside the window
            pipe.zremrangebyscore(key, "-inf", window_start)
            
            # Count current requests in window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {f"{now}:{time.time_ns()}": now})
            pipe.expire(key, config.window_seconds + 1)
            
            results = await pipe.execute()
            current_count = results[1]  # Count before adding current request
            
            if current_count >= config.max_requests:
                # Rate limit exceeded - remove the request we just added
                await redis_client.zrem(key, f"{now}:{time.time_ns()}")
                rate_limit_exceeded_total.labels(endpoint_type=endpoint_type, client_id=client_id).inc()
                return False, 0
            
            remaining = max(0, config.max_requests - current_count - 1)
            return True, remaining
            
        except Exception as e:
            logger.error("Redis rate limit check failed: %s", e)
            # Fallback to in-memory
            pass
    
    # In-memory fallback
    window = [t for t in _rate_store[key] if t > window_start]
    _rate_store[key] = window
    
    if len(window) >= config.max_requests:
        rate_limit_exceeded_total.labels(endpoint_type=endpoint_type, client_id=client_id).inc()
        return False, 0
    
    _rate_store[key].append(now)
    remaining = max(0, config.max_requests - len(window) - 1)
    return True, remaining


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_id = request.client.host if request.client else "anonymous"
        path = request.url.path
        method = request.method
        
        # Determine which rate limit config to use
        config = DEFAULT_RATE_LIMIT
        endpoint_type = "default"
        
        for endpoint_prefix, endpoint_config in CRITICAL_ENDPOINTS.items():
            if path.startswith(endpoint_prefix):
                config = endpoint_config
                endpoint_type = endpoint_prefix.split("/")[-1]
                break
        
        # Build rate limit key
        key = f"{RATE_LIMIT_PREFIX}{client_id}:{path}:{method}"
        
        # Check rate limit using sliding window
        allowed, remaining = await _check_rate_limit_sliding_window(key, config, client_id, endpoint_type)
        
        if not allowed:
            retry_after = config.window_seconds
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded for {endpoint_type}. Max {config.max_requests} requests per {config.window_seconds}s.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(config.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + config.window_seconds))
        
        return response
