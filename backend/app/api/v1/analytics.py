from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.analytics.ab_testing import ABTestService, FeatureFlagService
from app.services.analytics.funnel import FunnelService
from app.services.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/events")
async def track_event(
    event_name: str,
    project_id: UUID | None = None,
    properties: dict | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AnalyticsService(db)
    await service.track_event(
        event_name=event_name,
        user_id=current_user.id,
        project_id=project_id,
        properties=properties,
    )
    return {"tracked": True}


@router.post("/feedback/nps")
async def submit_nps(
    score: int,
    project_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AnalyticsService(db)
    await service.track_nps(current_user.id, score, project_id)
    return {"submitted": True}


@router.post("/feedback/csat")
async def submit_csat(
    score: int,
    project_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AnalyticsService(db)
    await service.track_csat(current_user.id, score, project_id)
    return {"submitted": True}


@router.get("/funnel/{funnel_name}")
async def get_funnel_stats(
    funnel_name: str,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    funnel_service = FunnelService(db)
    stats = await funnel_service.get_funnel_stats(funnel_name, days)
    return {"funnel": funnel_name, "stats": stats}


@router.get("/ab-test/{test_name}/variant")
async def get_ab_variant(
    test_name: str,
    variants: str = "A,B",
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ab_service = ABTestService(db)
    variant_list = [v.strip() for v in variants.split(",")]
    variant = await ab_service.get_variant(current_user.id, test_name, variant_list)
    return {"test_name": test_name, "variant": variant}


@router.post("/feature-flags/{flag_name}")
async def set_feature_flag(
    flag_name: str,
    enabled: bool,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    flag_service = FeatureFlagService(db)
    await flag_service.set_flag(current_user.id, flag_name, enabled)
    return {"flag": flag_name, "enabled": enabled}
