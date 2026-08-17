from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.schemas.recommendation import TemplateResponse, TemplateListResponse
from app.schemas.template_render import (
    RenderSceneRequest,
    RenderSceneResponse,
    RenderTemplateRequest,
    RenderTemplateResponse,
)
from app.services.recommendations.service import TemplateRepository
from app.services.templates.renderer import TemplateRenderer

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = TemplateRepository(db)
    templates, total = await repo.list_active(page=page, page_size=page_size)
    return TemplateListResponse(
        items=[TemplateResponse.model_validate(t) for t in templates],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = TemplateRepository(db)
    template = await repo.get_by_id(template_id)
    if template is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Шаблон не найден")
    return TemplateResponse.model_validate(template)


@router.post("/render", response_model=RenderTemplateResponse)
async def render_template(body: RenderTemplateRequest, db: AsyncSession = Depends(get_db)):
    renderer = TemplateRenderer(db)
    result = await renderer.render_template(body)
    renderer.validate_render(result)
    return result
