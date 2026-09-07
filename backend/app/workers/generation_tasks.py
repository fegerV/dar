import asyncio
import logging
from uuid import UUID

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.generation import Generation, GenerationJob
from app.workers.pipeline_tasks import execute_pipeline

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_generation_job(self, job_id: str):
    """Process a generation job by delegating to the real pipeline executor."""
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

        logger.info("Delegating generation %s to execute_pipeline", generation.id)
        execute_pipeline.delay(str(generation.id))
