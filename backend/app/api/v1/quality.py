from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundException
from app.models.quality import VideoCriticResult
from app.repositories.projects import ProjectRepository
from app.repositories.quality import QualityRepository
from app.schemas.quality import (
    ManualReviewRequest,
    ManualReviewResponse,
    QualityCheckRequest,
    QualityCheckResponse,
    QualityGateResponse,
    VideoCriticResponse,
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
        raise NotFoundException("Генерация не найдена")
    project = await ProjectRepository(db).get_by_id(generation.project_id, current_user.id)
    if project is None:
        raise NotFoundException("Доступ к генерации запрещён")
    output = generation.output_json or {}
    critic = None
    critic_model = await service.repo.get_critic_result(generation_id)
    if critic_model:
        critic = VideoCriticResponse(
            id=critic_model.id,
            generation_id=critic_model.generation_id,
            identity_score=critic_model.identity_score,
            motion_score=critic_model.motion_score,
            prompt_adherence=critic_model.prompt_adherence,
            face_quality=critic_model.face_quality,
            artifact_score=critic_model.artifact_score,
            overall=critic_model.overall,
            decision=critic_model.decision,
            created_at=critic_model.created_at,
        )
    return QualityGateResponse(
        generation_id=generation_id,
        status=generation.status,
        auto_checks_passed=output.get("auto_checks_passed", False),
        manual_review_required=generation.status == "review",
        final_status=generation.status,
        checks=[],
        critic=critic,
    )


@router.get("/generations/{generation_id}/critic", response_model=VideoCriticResponse)
async def get_critic_result(
    generation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = QualityGateService(db)
    generation = await service.repo.get_generation(generation_id)
    if generation is None:
        raise NotFoundException("Генерация не найдена")
    project = await ProjectRepository(db).get_by_id(generation.project_id, current_user.id)
    if project is None:
        raise NotFoundException("Доступ к генерации запрещён")
    critic = await service.repo.get_critic_result(generation_id)
    if critic is None:
        raise NotFoundException("Video Critic результат не найден")
    return VideoCriticResponse(
        id=critic.id,
        generation_id=critic.generation_id,
        identity_score=critic.identity_score,
        motion_score=critic.motion_score,
        prompt_adherence=critic.prompt_adherence,
        face_quality=critic.face_quality,
        artifact_score=critic.artifact_score,
        overall=critic.overall,
        decision=critic.decision,
        created_at=critic.created_at,
    )
