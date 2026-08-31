import asyncio
import logging
from datetime import UTC, datetime
from uuid import UUID

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.generation import Generation, GenerationJob, GenerationStep
from app.repositories.generations import GenerationRepository
from app.schemas.quality import QualityCheckRequest
from app.services.quality.service import QualityGateService
from app.workers.utils import estimate_eta, upload_placeholder_video

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_generation_job(self, job_id: str):
    asyncio.run(_process_generation_job(job_id))


async def _process_generation_job(job_id: str):
    job_uuid = UUID(job_id)
    async with async_session() as db:
        result = await db.execute(
            select(GenerationJob).where(GenerationJob.id == job_uuid)
        )
        job = result.scalar_one_or_none()
        if job is None:
            logger.error("Job not found: %s", job_id)
            return

        result = await db.execute(
            select(Generation).where(Generation.id == job.generation_id)
        )
        generation = result.scalar_one_or_none()
        if generation is None:
            logger.error("Generation not found for job: %s", job_id)
            return

        generation.status = "processing"
        generation.started_at = datetime.now(UTC)
        await db.flush()

        steps = await _get_steps(db, generation.id)
        total_steps = len(steps)

        for idx, step in enumerate(steps):
            step.status = "processing"
            step.started_at = datetime.now(UTC)
            await db.flush()

            await asyncio.sleep(2)

            step.status = "completed"
            step.output_json = {"result": "ok"}
            step.completed_at = datetime.now(UTC)
            await db.flush()

            generation.progress = int((idx + 1) / total_steps * 100)
            generation.current_step = step.step_code
            generation.estimated_seconds = estimate_eta(steps, idx)
            await db.flush()

        generation.status = "completed"
        generation.progress = 100
        generation.completed_at = datetime.now(UTC)
        try:
            urls = await upload_placeholder_video(generation)
        except Exception as e:
            logger.warning("Storage upload failed for %s: %s", generation.id, e)
            urls = {
                "video_url": None,
                "thumbnail_url": None,
            }
        generation.output_json = {
            "video_url": urls["video_url"],
            "thumbnail_url": urls["thumbnail_url"],
            "duration_sec": 30,
            "resolution": [1920, 1080],
            "fps": 30,
            "audio_ok": True,
            "face_count": 1,
        }
        job.status = "finished"
        job.finished_at = datetime.now(UTC)
        await db.commit()
        logger.info("Generation %s completed", generation.id)

        try:
            quality = QualityGateService(db)
            quality_request = QualityCheckRequest(
                generation_id=generation.id,
                asset_ids=[],
                prompt=(generation.input_json or {}).get("prompt", "") if isinstance(generation.input_json, dict) else "",
            )
            await quality.run_quality_checks(quality_request)
        except Exception as e:  # noqa: BLE001
            logger.warning("Quality gate failed for %s: %s", generation.id, e)
            generation.status = "completed"
            await GenerationRepository(db).update(generation)
            await db.commit()


async def _get_steps(db, generation_id: UUID) -> list[GenerationStep]:
    result = await db.execute(
        select(GenerationStep)
        .where(GenerationStep.generation_id == generation_id)
        .order_by(GenerationStep.step_no.asc())
    )
    return list(result.scalars().all())
