from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.pipeline import PipelineRunRequest, PipelineRunResponse
from app.services.pipeline.orchestrator import PipelineOrchestrator

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


@router.post("/projects/{project_id}/run", response_model=PipelineRunResponse)
async def run_pipeline(
    project_id: UUID,
    body: PipelineRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    orchestrator = PipelineOrchestrator(db)
    return await orchestrator.run(body, current_user.id)
