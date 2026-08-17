from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.quality import (
    ManualReviewRequest,
    ManualReviewResponse,
    QualityCheckRequest,
    QualityCheckResponse,
    QualityGateResponse,
)
from app.services.quality.service import QualityGateService

router = APIRouter(prefix="/quality", tags=["Quality"])


@router.post("/checks", response_model=QualityGateResponse)
async def run_quality_checks(
    body: QualityCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = QualityGateService(db)
    return await service.run_quality_checks(body)


@router.post("/generations/{generation_id}/review", response_model=ManualReviewResponse)
async def submit_manual_review(
    generation_id: UUID,
    body: ManualReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = QualityGateService(db)
    return await service.submit_manual_review(generation_id, body)


@router.get("/generations/{generation_id}", response_model=QualityGateResponse)
async def get_quality_status(
    generation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = QualityGateService(db)
    generation = await service.repo.get_generation(generation_id)
    if generation is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Генерация не найдена")
    output = generation.output_json or {}
    return QualityGateResponse(
        generation_id=generation_id,
        status=generation.status,
        auto_checks_passed=output.get("auto_checks_passed", False),
        manual_review_required=generation.status == "review",
        final_status=generation.status,
        checks=[],
    )
