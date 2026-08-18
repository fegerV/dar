from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.template import TemplateVersion

router = APIRouter(prefix="/ab-tests", tags=["A/B Testing"])


@router.get("/templates/{template_id}/variants")
async def list_template_variants(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(TemplateVersion).where(
            TemplateVersion.template_id == template_id,
            TemplateVersion.variant_group.is_not(None),
        )
    )
    variants = result.scalars().all()
    return [
        {
            "version_id": str(v.id),
            "variant_group": v.variant_group,
            "variant_name": v.variant_name,
            "status": v.status,
        }
        for v in variants
    ]
