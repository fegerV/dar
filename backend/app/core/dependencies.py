from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.repositories.users import UserRepository

bearer_scheme = HTTPBearer()


def get_client_ip(request: Request) -> str | None:
    """Resolve the caller IP, honouring the left-most X-Forwarded-For entry."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        first = forwarded_for.split(",")[0].strip()
        if first:
            return first
    return request.client.host if request.client else None


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UUID:
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise UnauthorizedException("Invalid or expired token")
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Invalid token payload")
    return UUID(user_id)


async def get_current_user(
    request: Request,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None or user.status != "active":
        raise UnauthorizedException("User not found or inactive")

    blocked_ips = (user.metadata_ or {}).get("blocked_ips") or []
    if blocked_ips:
        client_ip = get_client_ip(request)
        if client_ip and client_ip in blocked_ips:
            raise ForbiddenException("Access from this IP address is blocked")

    return user


async def get_current_user_optional(request: Request) -> object | None:
    auth = request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        return None
    token = auth.split(" ", 1)[1]
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    try:
        async for db in get_db():
            repo = UserRepository(db)
            user = await repo.get_by_id(UUID(user_id))
            return user
    except Exception:
        return None
    return None
