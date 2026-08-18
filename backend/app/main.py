import shutil

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.lifespan import lifespan
from app.middleware.csrf import CSRFMiddleware
from app.middleware.audit import AuditMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIdMiddleware

app = FastAPI(
    title="DarAgent API",
    version="0.1.0",
    description="AI-сервис персональных видеопоздравлений",
    lifespan=lifespan,
)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.api.v1.router import v1_router

app.include_router(v1_router)


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
    return {
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
        },
    }
