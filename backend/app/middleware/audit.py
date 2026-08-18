import logging
from uuid import UUID

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.audit import AuditLog

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        try:
            path = request.url.path
            method = request.method
            if method in ("POST", "PATCH", "DELETE", "PUT"):
                actor_id = None
                auth = request.headers.get("authorization")
                if auth and auth.lower().startswith("bearer "):
                    from app.core.security import decode_token
                    token = auth.split(" ", 1)[1]
                    payload = decode_token(token)
                    if payload and payload.get("type") == "access":
                        try:
                            actor_id = UUID(payload.get("sub"))
                        except (ValueError, TypeError):
                            actor_id = None

                target_type = None
                target_id = None
                parts = path.strip("/").split("/")
                if len(parts) >= 3 and parts[0] == "api" and parts[1] == "v1":
                    resource = parts[2]
                    target_type = resource.rstrip("s")
                    if len(parts) >= 4 and parts[3] not in ("me", "stream", "entitlements", "audit-logs"):
                        try:
                            target_id = UUID(parts[3])
                        except ValueError:
                            target_id = None
                ip = request.client.host if request.client else None
                ua = request.headers.get("user-agent")

                async with async_session_factory() as session:
                    stmt = insert(AuditLog).values(
                        actor_user_id=actor_id,
                        action=f"{method}:{path}",
                        target_type=target_type,
                        target_id=target_id,
                        ip_address=ip,
                        user_agent=ua,
                        metadata={},
                    )
                    await session.execute(stmt)
                    await session.commit()
        except Exception as exc:
            logger.debug("Audit middleware skipped: %s", exc)
        return response
