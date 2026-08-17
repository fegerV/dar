from contextlib import asynccontextmanager

from app.core.config import settings


@asynccontextmanager
async def lifespan(app):
    if settings.APP_DEBUG:
        print(f"DarAgent starting in {settings.APP_ENV} mode")
    yield
    if settings.APP_DEBUG:
        print("DarAgent shutting down")
