"""Celery tasks for the MVP generation pipeline.

The HTTP API currently executes the mock pipeline synchronously for a fast
backend-first slice. This worker task keeps the async boundary ready for Docker
and future real providers.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone, UTC
from decimal import Decimal
from typing import Any
from uuid import UUID

from ai_providers.router import ai_router
from core.database import async_session_maker
from models import Asset, Generation, GenerationOutput, GenerationStep, Project, StorageObject
from workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def run_generation_pipeline(self, generation_id: str) -> dict[str, Any]:
    try:
        return asyncio.run(_execute_generation_pipeline(UUID(generation_id)))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60) from None


async def _execute_generation_pipeline(generation_id: UUID) -> dict[str, Any]:
    async with async_session_maker() as session:
        generation = await session.get(Generation, generation_id)
        if not generation:
            raise ValueError(f"Generation {generation_id} not found")
        project = await session.get(Project, generation.project_id)
        if not project:
            raise ValueError(f"Project {generation.project_id} not found")

        generation.status = "processing"
        generation.started_at = datetime.now(UTC)
        steps = [(1, "compile_prompt", "script"), (2, "mock_video", "video"), (3, "quality_check", "final")]
        for no, code, kind in steps:
            generation.current_step = code
            generation.progress = min(95, no * 30)
            session.add(
                GenerationStep(
                    generation_id=generation.id,
                    step_no=no,
                    step_code=code,
                    type=kind,
                    status="completed",
                    input_json={"project_id": str(project.id)},
                    output_json={"mock": True},
                    completed_at=datetime.now(UTC),
                )
            )
            await session.flush()

        result = await ai_router.get_video_provider().generate_video(
            prompt=f"Mock DarAgent video for {project.title or project.occasion_code}",
            duration=10,
        )
        storage = StorageObject(
            bucket="daragent",
            object_key=f"generations/{generation.id}/result.mp4",
            mime_type="video/mp4",
            size_bytes=1024,
            metadata_json=result,
        )
        session.add(storage)
        await session.flush()
        asset = Asset(
            owner_user_id=project.owner_user_id,
            type="video",
            status="ready",
            storage_object_id=storage.id,
            title="result.mp4",
            mime_type="video/mp4",
            duration_sec=Decimal("10"),
            url=result["video_url"],
        )
        session.add(asset)
        await session.flush()
        session.add(GenerationOutput(generation_id=generation.id, asset_id=asset.id, role="final_video"))
        generation.status = "completed"
        generation.progress = 100
        generation.current_step = None
        generation.completed_at = datetime.now(UTC)
        project.status = "ready"
        await session.commit()
        return {"generation_id": str(generation.id), "status": generation.status}
