import logging
import shutil
from datetime import UTC

from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings
from app.core.database import async_session_factory, engine
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException
from app.core.lifespan import lifespan
from app.middleware.audit import AuditMiddleware
from app.middleware.csrf import CSRFMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIdMiddleware

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


if settings.APP_ENV == "production":
    if not settings.YOOKASSA_SHOP_ID or not settings.YOOKASSA_SECRET_KEY:
        raise RuntimeError(
            "Production mode requires YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY. "
            "Mock payment mode is disabled in production."
        )

app = FastAPI(
    title="DarAgent API",
    version="0.1.0",
    description="AI-сервис персональных видеопоздравлений",
    lifespan=lifespan,
)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/detailed")
async def health_detailed():
    db_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    disk = shutil.disk_usage("/")
    disk_used_percent = (disk.used / disk.total) * 100 if disk.total > 0 else 0

    monitoring_ok = True
    metrics = {}
    try:
        async with async_session_factory() as session:
            from app.services.monitoring.service import MonitoringService
            monitor = MonitoringService(session)
            metrics = await monitor.collect_system_metrics()
    except Exception:
        monitoring_ok = False

    from app.integrations.ai.registry import create_provider_registry

    registry = create_provider_registry()
    ai_providers_status = {}
    ai_ok = True
    provider_attrs = (
        "text_providers",
        "image_providers",
        "video_providers",
        "voice_providers",
        "music_providers",
    )
    for attr in provider_attrs:
        providers = getattr(registry, attr, [])
        for p in providers:
            try:
                healthy = await p.healthcheck()
                ai_providers_status[f"{p.name}"] = healthy
                if not healthy:
                    ai_ok = False
            except Exception:
                ai_providers_status[f"{p.name}"] = False
                ai_ok = False

    storage_ok = True
    try:
        from app.integrations.storage.factory import get_storage_provider
        storage = get_storage_provider()
        storage_ok = await storage.healthcheck()
    except Exception:
        storage_ok = False

    redis_ok = metrics.get("components", {}).get("redis", False)

    return {
        "status": "ok" if (db_ok and monitoring_ok and ai_ok and storage_ok) else "degraded",
        "database": db_ok,
        "redis": redis_ok,
        "ai_providers": ai_providers_status,
        "storage": storage_ok,
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "used_percent": disk_used_percent,
        },
        "disk_alert": disk_used_percent > 90,
        "queue_depth": metrics.get("queue_depth", {}),
        "user_count": metrics.get("user_count", 0),
        "components": {
            "database": int(db_ok),
            "redis": int(redis_ok),
            "ai": int(ai_ok),
            "storage": int(storage_ok),
            "disk": int(disk_used_percent < 90),
        },
    }


@app.get("/metrics")
async def metrics():
    from app.services.monitoring.service import MonitoringService

    async with async_session_factory() as session:
        monitor = MonitoringService(session)
        await monitor.collect_system_metrics()
        return Response(content=monitor.get_metrics(), media_type=MonitoringService.CONTENT_TYPE)


from app.api.v1.router import v1_router  # noqa: E402

app.include_router(v1_router)


@app.get("/admin/events/stream")
async def admin_events_stream(request: Request, current_user=Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise ForbiddenException("Admin access required")

    import asyncio
    import json
    from datetime import datetime

    async def event_generator():
        yield "retry: 5000\n\n"
        while True:
            if await request.is_disconnected():
                break
            try:
                async with async_session_factory() as session:
                    from app.services.admin.service import AdminService
                    service = AdminService(session)
                    stats = await service.get_dashboard_stats()
                    yield f"data: {json.dumps({'type': 'stats', 'data': stats.model_dump(mode='json'), 'timestamp': datetime.now(UTC).isoformat()})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e), 'timestamp': datetime.now(UTC).isoformat()})}\n\n"
            await asyncio.sleep(5)

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive"})
