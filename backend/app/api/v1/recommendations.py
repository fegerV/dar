from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.recommendation import (
    RecommendationListResponse,
    RecommendationSelectResponse,
)
from app.services.recommendations.service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/projects/{project_id}/generate", response_model=RecommendationListResponse)
async def generate_recommendations(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RecommendationService(db)
    return await service.generate(project_id)


@router.get("/projects/{project_id}", response_model=RecommendationListResponse)
async def list_recommendations(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RecommendationService(db)
    return await service.list(project_id)


@router.post(
    "/projects/{project_id}/select/{recommendation_id}",
    response_model=RecommendationSelectResponse,
)
async def select_recommendation(
    project_id: UUID,
    recommendation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RecommendationService(db)
    return await service.select(project_id, recommendation_id)
