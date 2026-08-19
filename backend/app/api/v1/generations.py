from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.generation import (
    GenerationListResponse,
    GenerationResponse,
    GenerationStartRequest,
)
from app.services.generations.service import GenerationService

router = APIRouter(prefix="/generations", tags=["Generations"])


@router.post("/projects/{project_id}", response_model=GenerationResponse)
async def start_generation(
    project_id: UUID,
    body: GenerationStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = GenerationService(db)
    return await service.start_generation(project_id, current_user.id, body)


@router.get("/projects/{project_id}", response_model=GenerationListResponse)
async def list_generations(
    project_id: UUID,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = GenerationService(db)
    items, total = await service.list_generations(project_id, current_user.id, page, page_size)
    return GenerationListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{generation_id}", response_model=GenerationResponse)
async def get_generation(
    generation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = GenerationService(db)
    return await service.get_generation(generation_id, current_user.id)


@router.post("/{generation_id}/cancel", response_model=GenerationResponse)
async def cancel_generation(
    generation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = GenerationService(db)
    return await service.cancel_generation(generation_id, current_user.id)
