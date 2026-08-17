import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.generation import Generation, GenerationJob, GenerationStep

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def execute_pipeline(self, generation_id: str):
    asyncio.run(_execute_pipeline(generation_id))


async def _execute_pipeline(generation_id: str):
    gen_uuid = UUID(generation_id)
    async with async_session() as db:
        result = await db.execute(
            __import__("sqlalchemy").select(Generation).where(Generation.id == gen_uuid)
        )
        generation = result.scalar_one_or_none()
        if generation is None:
            logger.error("Generation not found: %s", generation_id)
            return

        generation.status = "processing"
        generation.started_at = datetime.now(timezone.utc)
        await db.commit()

        result = await db.execute(
            __import__("sqlalchemy").select(GenerationStep)
            .where(GenerationStep.generation_id == gen_uuid)
            .order_by(GenerationStep.step_no.asc())
        )
        steps = list(result.scalars().all())
        total = len(steps)

        for idx, step in enumerate(steps):
            step.status = "processing"
            step.started_at = datetime.now(timezone.utc)
            await db.commit()

            await asyncio.sleep(2)

            step.status = "completed"
            step.output_json = {"result": "ok", "step": step.step_code}
            step.completed_at = datetime.now(timezone.utc)
            await db.commit()

            generation.progress = int((idx + 1) / total * 100)
            generation.current_step = step.step_code
            await db.commit()

        generation.status = "completed"
        generation.progress = 100
        generation.completed_at = datetime.now(timezone.utc)
        generation.output_json = {
            "video_url": "http://localhost:9000/daragent/outputs/final.mp4",
            "thumbnail_url": "http://localhost:9000/daragent/outputs/thumb.jpg",
            "duration_sec": 30,
            "resolution": [1920, 1080],
            "fps": 30,
            "audio_ok": True,
        }

        result = await db.execute(
            __import__("sqlalchemy").select(GenerationJob)
            .where(GenerationJob.generation_id == gen_uuid)
            .order_by(GenerationJob.created_at.asc())
            .limit(1)
        )
        job = result.scalar_one_or_none()
        if job:
            job.status = "finished"
            job.finished_at = datetime.now(timezone.utc)

        await db.commit()
        logger.info("Pipeline %s completed", generation_id)
