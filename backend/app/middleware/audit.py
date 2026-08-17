import logging
from uuid import UUID

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.dependencies import get_current_user_optional

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        try:
            path = request.url.path
            method = request.method
            if method in ("POST", "PATCH", "DELETE", "PUT"):
                user = await get_current_user_optional(request)
                actor_id = getattr(user, "id", None) if user else None
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
                logger.info(
                    "AUDIT %s %s %s %s %s",
                    actor_id,
                    method,
                    path,
                    target_type,
                    target_id,
                )
        except Exception as exc:  # pragma: no cover
            logger.debug("Audit middleware skipped: %s", exc)
        return response
