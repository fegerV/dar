from fastapi import APIRouter

from app.api.v1.assets import router as assets_router
from app.api.v1.auth import router as auth_router
from app.api.v1.payments import router as payments_router
from app.api.v1.recipients import router as recipients_router
from app.api.v1.projects import router as projects_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.templates import router as templates_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router)
v1_router.include_router(recipients_router)
v1_router.include_router(projects_router)
v1_router.include_router(recommendations_router)
v1_router.include_router(templates_router)
v1_router.include_router(assets_router)
v1_router.include_router(payments_router)
