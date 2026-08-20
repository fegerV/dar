from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.brief import (
    BriefCompleteResponse,
    BriefQuestionsResponse,
    BriefSummaryResponse,
    BriefUpdate,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.projects.service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectService(db)
    return await service.create(current_user.id, body)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectService(db)
    items, total = await service.list(current_user.id, page, page_size, status)
    return ProjectListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectService(db)
    return await service.get(current_user.id, project_id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    body: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectService(db)
    return await service.update(current_user.id, project_id, body)


@router.get("/{project_id}/brief", response_model=BriefUpdate)
async def get_brief(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectService(db)
    return await service.get_brief(current_user.id, project_id)


@router.put("/{project_id}/brief", response_model=BriefUpdate)
async def save_brief(
    project_id: UUID,
    body: BriefUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectService(db)
    return await service.save_brief(current_user.id, project_id, body)


@router.post("/{project_id}/brief/complete", response_model=BriefCompleteResponse)
async def complete_brief(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectService(db)
    return await service.complete_brief(current_user.id, project_id)


@router.get("/{project_id}/brief/questions", response_model=BriefQuestionsResponse)
async def get_brief_questions(
    project_id: UUID,
    relationship: str | None = Query(None),
    occasion_code: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectService(db)
    return await service.get_brief_questions(
        current_user.id, project_id, relationship, occasion_code
    )


@router.get("/{project_id}/brief/summary", response_model=BriefSummaryResponse)
async def get_brief_summary(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ProjectService(db)
    return await service.get_brief_summary(current_user.id, project_id)
