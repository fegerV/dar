from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundException
from app.services.templates.versioning import TemplateVersionService

router = APIRouter(prefix="/template-versions", tags=["Template Versioning & QA"])


class VersionUpdateRequest:
    pass


@router.post("/templates/{template_id}/versions", response_model=dict)
async def create_version(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TemplateVersionService(db)
    version = await service.create_version(template_id, current_user.id)
    await db.commit()
    await db.refresh(version)
    return {
        "id": str(version.id),
        "version": version.version,
        "status": version.status,
        "template_id": str(template_id),
        "created_at": version.created_at.isoformat() if version.created_at else None,
    }


@router.patch("/versions/{version_id}", response_model=dict)
async def update_version(
    version_id: UUID,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TemplateVersionService(db)
    version = await service.update_version(
        version_id,
        current_user.id,
        prompt_config=body.get("prompt_config"),
        render_config=body.get("render_config"),
        personalization_config=body.get("personalization_config"),
        validation_config=body.get("validation_config"),
        max_duration_sec=body.get("max_duration_sec"),
        qa_checklist=body.get("qa_checklist"),
    )
    await db.commit()
    await db.refresh(version)
    return {
        "id": str(version.id),
        "version": version.version,
        "status": version.status,
        "max_duration_sec": version.max_duration_sec,
        "qa_checklist": version.qa_checklist,
    }


@router.post("/versions/{version_id}/transition", response_model=dict)
async def transition_status(
    version_id: UUID,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    new_status = body.get("status")
    if not new_status:
        from app.core.exceptions import ValidationException
        raise ValidationException("status field is required")
    service = TemplateVersionService(db)
    version = await service.transition_status(version_id, current_user.id, new_status)
    await db.commit()
    await db.refresh(version)
    return {
        "id": str(version.id),
        "version": version.version,
        "status": version.status,
        "published_at": version.published_at.isoformat() if version.published_at else None,
        "retired_at": version.retired_at.isoformat() if version.retired_at else None,
    }


@router.get("/templates/{template_id}/versions", response_model=list[dict])
async def list_versions(
    template_id: UUID,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TemplateVersionService(db)
    versions = await service.list_versions(template_id, current_user.id, status)
    return [
        {
            "id": str(v.id),
            "version": v.version,
            "status": v.status,
            "schema_version": v.schema_version,
            "max_duration_sec": v.max_duration_sec,
            "published_at": v.published_at.isoformat() if v.published_at else None,
            "retired_at": v.retired_at.isoformat() if v.retired_at else None,
            "qa_checklist": v.qa_checklist,
        }
        for v in versions
    ]


@router.get("/versions/{version_id}", response_model=dict)
async def get_version(
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TemplateVersionService(db)
    version = await service.get_version(version_id, current_user.id)
    if version is None:
        raise NotFoundException("Version not found")
    return {
        "id": str(version.id),
        "version": version.version,
        "status": version.status,
        "schema_version": version.schema_version,
        "prompt_config": version.prompt_config,
        "render_config": version.render_config,
        "personalization_config": version.personalization_config,
        "validation_config": version.validation_config,
        "max_duration_sec": version.max_duration_sec,
        "published_at": version.published_at.isoformat() if version.published_at else None,
        "retired_at": version.retired_at.isoformat() if version.retired_at else None,
        "qa_checklist": version.qa_checklist,
        "variant_group": version.variant_group,
        "variant_name": version.variant_name,
    }
