from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundException
from app.models.generation import Generation
from app.models.intelligence import GenerationFailure, UserFeedback
from app.schemas.intelligence import (
    GenerationFailureResponse,
    ImagePreflightRequest,
    ImagePreflightResponse,
    UserFeedbackRequest,
    UserFeedbackResponse,
    VideoRecipeResponse,
)
from app.services.intelligence.failure_analyzer import RecipeService
from app.services.intelligence.preflight import ImagePreflightService

router = APIRouter(prefix="/intelligence", tags=["Intelligence"])


@router.post("/preflight", response_model=ImagePreflightResponse)
async def analyze_image(
    body: ImagePreflightRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ImagePreflightService(db)
    return await service.analyze(body.generation_id, body.image_url, body.image_metadata, current_user.id)


@router.get("/recipes/{recipe_code}", response_model=VideoRecipeResponse)
async def get_recipe(
    recipe_code: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.core.exceptions import ForbiddenException

    if not getattr(current_user, "is_admin", False):
        raise ForbiddenException("Admin access required")
    service = RecipeService(db)
    recipe = await service.get_best_recipe(recipe_code)
    if recipe is None:
        raise NotFoundException("Recipe not found")
    return VideoRecipeResponse.model_validate(recipe)


@router.get("/generations/{generation_id}/failure", response_model=GenerationFailureResponse)
async def get_generation_failure(
    generation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    gen_result = await db.execute(
        select(Generation).where(Generation.id == generation_id)
    )
    generation = gen_result.scalar_one_or_none()
    if generation is None:
        raise NotFoundException("Generation not found")

    from app.repositories.projects import ProjectRepository
    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(generation.project_id, current_user.id)
    if project is None:
        raise NotFoundException("Generation not found")

    failure_result = await db.execute(
        select(GenerationFailure).where(GenerationFailure.generation_id == generation_id)
    )
    failure = failure_result.scalar_one_or_none()
    if failure is None:
        raise NotFoundException("Failure analysis not found")
    return GenerationFailureResponse.model_validate(failure)


@router.post("/feedback", response_model=UserFeedbackResponse)
async def submit_feedback(
    body: UserFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    gen_result = await db.execute(
        select(Generation).where(Generation.id == body.generation_id)
    )
    generation = gen_result.scalar_one_or_none()
    if generation is None:
        raise NotFoundException("Generation not found")

    from app.repositories.projects import ProjectRepository
    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(generation.project_id, current_user.id)
    if project is None:
        raise NotFoundException("Generation not found")

    feedback = UserFeedback(
        generation_id=body.generation_id,
        rating=body.rating,
        reason=body.reason,
        comment=body.comment,
    )
    db.add(feedback)
    await db.flush()
    await db.commit()
    return UserFeedbackResponse.model_validate(feedback)
