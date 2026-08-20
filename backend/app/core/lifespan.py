from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import async_session_factory
from app.services.admin.service import AdminService


@asynccontextmanager
async def lifespan(app):
    if settings.APP_DEBUG:
        print(f"DarAgent starting in {settings.APP_ENV} mode")
    async with async_session_factory() as session:
        service = AdminService(session)
        await service.ensure_default_settings()
    yield
    if settings.APP_DEBUG:
        print("DarAgent shutting down")
