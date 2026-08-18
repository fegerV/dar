import re

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


CSRF_PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

_API_PREFIX = re.compile(r"^/api/v\d+/admin/")


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method in CSRF_PROTECTED_METHODS:
            path = request.url.path
            if _API_PREFIX.match(path):
                if not request.headers.get("X-Requested-With"):
                    return Response(
                        status_code=403,
                        content='{"detail": "CSRF: missing X-Requested-With header"}',
                        media_type="application/json",
                    )
        return await call_next(request)
