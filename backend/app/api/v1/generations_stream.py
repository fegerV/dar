import asyncio
import json
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundException
from app.repositories.generations import GenerationRepository
from app.repositories.projects import ProjectRepository

router = APIRouter(prefix="/generations", tags=["Generations"])


@router.get("/{generation_id}/stream")
async def stream_generation_progress(
    generation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    repo = GenerationRepository(db)
    project_repo = ProjectRepository(db)
    generation = await repo.get_by_id(generation_id)
    if generation is None:
        raise NotFoundException("Генерация не найдена")

    project = await project_repo.get_by_id(generation.project_id, current_user.id)
    if project is None:
        raise NotFoundException("Генерация не найдена")

    async def event_stream():
        last_progress = -1
        max_iterations = 300
        iteration = 0

        while iteration < max_iterations:
            await db.refresh(generation)
            steps = await repo.get_steps(generation_id)

            progress = generation.progress or 0
            current_step = generation.current_step or "queued"
            status = generation.status or "created"
            estimated_seconds = generation.estimated_seconds

            if progress != last_progress:
                payload = {
                    "generation_id": str(generation_id),
                    "status": status,
                    "progress": progress,
                    "current_step": current_step,
                    "estimated_seconds": estimated_seconds,
                    "steps": [
                        {
                            "step_no": s.step_no,
                            "step_code": s.step_code,
                            "type": s.type,
                            "status": s.status,
                            "created_at": s.created_at.isoformat() if s.created_at else None,
                            "started_at": s.started_at.isoformat() if s.started_at else None,
                            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                        }
                        for s in steps
                    ],
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                yield f"data: {json.dumps(payload)}\n\n"
                last_progress = progress

            if status in ("completed", "failed", "cancelled", "approved", "rejected"):
                break

            await asyncio.sleep(1)
            iteration += 1

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
