from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.generation import Generation
from app.models.project import Project
from app.services.script_generation.service import ScriptGenerationService

router = APIRouter(prefix="/generations", tags=["Generations"])


@router.post("/{generation_id}/script", response_model=dict)
async def generate_script(
    generation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    gen_result = await db.execute(
        select(Generation).where(Generation.id == generation_id)
    )
    generation = gen_result.scalar_one_or_none()
    if generation is None:
        raise HTTPException(status_code=404, detail="Generation not found")

    proj_result = await db.execute(
        select(Project).where(
            Project.id == generation.project_id,
            Project.owner_user_id == current_user.id,
        )
    )
    project = proj_result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    service = ScriptGenerationService(db)
    result = await service.generate_script(
        project_id=project.id,
        owner_user_id=current_user.id,
        generation_step_id=generation_id,
    )
    return result
