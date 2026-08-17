from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.assets import router as assets_router
from app.api.v1.auth import router as auth_router
from app.api.v1.account import router as account_router
from app.api.v1.contacts import router as contacts_router
from app.api.v1.delivery import router as delivery_router
from app.api.v1.generations import router as generations_router
from app.api.v1.generations_stream import router as generations_stream_router
from app.api.v1.holidays import router as holidays_router
from app.api.v1.payments import router as payments_router
from app.api.v1.pipeline import router as pipeline_router
from app.api.v1.pricing import router as pricing_router
from app.api.v1.prompt_compiler import router as prompt_compiler_router
from app.api.v1.quality import router as quality_router
from app.api.v1.referrals import router as referrals_router
from app.api.v1.recipients import router as recipients_router
from app.api.v1.projects import router as projects_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.share import router as share_router
from app.api.v1.templates import router as templates_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router)
v1_router.include_router(recipients_router)
v1_router.include_router(projects_router)
v1_router.include_router(recommendations_router)
v1_router.include_router(templates_router)
v1_router.include_router(assets_router)
v1_router.include_router(generations_router)
v1_router.include_router(generations_stream_router)
v1_router.include_router(holidays_router)
v1_router.include_router(referrals_router)
v1_router.include_router(quality_router)
v1_router.include_router(payments_router)
v1_router.include_router(delivery_router)
v1_router.include_router(share_router)
v1_router.include_router(prompt_compiler_router)
v1_router.include_router(pipeline_router)
v1_router.include_router(pricing_router)
v1_router.include_router(analytics_router)
v1_router.include_router(admin_router)
v1_router.include_router(account_router)
v1_router.include_router(contacts_router)
