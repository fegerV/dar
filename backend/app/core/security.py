import secrets
import time
from datetime import UTC, datetime, timedelta
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


# Token blacklist storage (Redis-backed)
_TOKEN_BLACKLIST_PREFIX = "daragent:token_blacklist:"


async def blacklist_token(token: str, exp: float) -> bool:
    """Add token to blacklist until its expiration."""
    try:
        import redis.asyncio as redis
        from app.core.config import settings
        
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        ttl = max(int(exp - time.time()), 1)
        await redis_client.set(f"{_TOKEN_BLACKLIST_PREFIX}{token}", "1", ex=ttl)
        return True
    except Exception:
        return False


async def is_token_blacklisted(token: str) -> bool:
    """Check if token is in blacklist."""
    try:
        import redis.asyncio as redis
        from app.core.config import settings
        
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        result = await redis_client.get(f"{_TOKEN_BLACKLIST_PREFIX}{token}")
        return result is not None
    except Exception:
        return False


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: UUID, jti: str | None = None) -> str:
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": now,
        "nbf": now,
        "type": "access",
        "jti": jti or secrets.token_urlsafe(32),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: UUID, jti: str | None = None) -> str:
    now = datetime.now(UTC)
    expire = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    jti_val = jti or secrets.token_urlsafe(32)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": now,
        "type": "refresh",
        "jti": jti_val,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, validate_iat: bool = True, check_blacklist: bool = True) -> dict | None:
    """Decode and validate JWT token with iat and blacklist checks."""
    try:
        # First decode without verification to get claims
        unverified = jwt.get_unverified_claims(token)
        
        # Check if token is blacklisted
        if check_blacklist and is_token_blacklisted(token):
            return None
        
        # Validate iat (issued at) - reject tokens older than max age
        if validate_iat:
            iat = unverified.get("iat")
            if iat is None:
                return None
            
            # Convert iat to timestamp if it's a datetime
            if isinstance(iat, datetime):
                iat_timestamp = iat.timestamp()
            else:
                iat_timestamp = float(iat)
            
            now = time.time()
            max_token_age = timedelta(hours=24).total_seconds()  # Configurable max age
            
            if now - iat_timestamp > max_token_age:
                return None  # Token too old
        
        # Now do full verification
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
    except (ValueError, TypeError):
        return None


def create_impersonation_token(user_id: UUID, actor_id: UUID) -> str:
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=5)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": now,
        "type": "impersonation",
        "actor_id": str(actor_id),
        "watermark": True,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
