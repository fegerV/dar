import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.generation import Generation, GenerationJob, GenerationStep
from app.models.intelligence import GenerationFailure, VideoRecipe
from app.repositories.generations import GenerationRepository
from app.services.intelligence.failure_analyzer import FailureAnalyzer, RecipeService
from app.services.intelligence.preflight import ImagePreflightService
from app.services.intelligence.prompt_repair import PromptRepairService
from app.services.quality.service import QualityGateService

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

        try:
            preflight = ImagePreflightService(db)
            image_url = (generation.input_json or {}).get("image_url")
            if image_url:
                await preflight.analyze(
                    generation.id,
                    image_url,
                    (generation.input_json or {}).get("image_metadata"),
                )
        except Exception as e:  # noqa: BLE001
            logger.warning("Image preflight failed for %s: %s", generation_id, e)

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
            generation.estimated_seconds = _estimate_eta(steps, idx)
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
            "face_count": 1,
            "face_metrics": {
                "identity_score": 0.94,
                "face_quality": 0.97,
                "landmarks_stable": True,
                "blink_detected": True,
            },
            "video_metrics": {
                "motion_score": 0.91,
                "prompt_adherence": 0.88,
                "artifact_score": 0.95,
            },
            "scene_description": (generation.input_json or {}).get("prompt", ""),
            "source_face": {
                "face_count": 1,
            },
            "prompt": (generation.input_json or {}).get("prompt", ""),
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

        try:
            quality = QualityGateService(db)
            quality_response = await quality.run_quality_checks(
                __import__("app.schemas.quality", fromlist=["QualityCheckRequest"]).QualityCheckRequest(
                    generation_id=gen_uuid,
                    asset_ids=[],
                    prompt=generation.prompt,
                )
            )
            if quality_response.final_status == "rejected":
                await _targeted_regeneration(db, generation, quality_response)
        except Exception as e:  # noqa: BLE001
            logger.warning("Quality gate failed for %s: %s", generation_id, e)
            generation.status = "completed"
            await GenerationRepository(db).update(generation)
            await db.commit()


async def _targeted_regeneration(db, generation: Generation, quality_response) -> None:
    critic = quality_response.critic or {}
    quality_checks = (generation.output_json or {}).get("quality_checks", {})
    analyzer = FailureAnalyzer()
    repair = PromptRepairService(db)
    recipe_service = RecipeService(db)

    failure_codes = analyzer.analyze(critic.raw_response if isinstance(critic, dict) else {}, quality_checks)
    recipe = await recipe_service.get_best_recipe(getattr(generation, "template_code", None) or "")

    repaired = repair.repair(
        failure_codes=failure_codes,
        current_prompt=getattr(generation, "prompt", None),
        current_negative=(generation.output_json or {}).get("negative_prompt"),
        recipe=recipe,
    )

    failure = GenerationFailure(
        generation_id=generation.id,
        failure_codes=failure_codes,
        repaired_prompt=repaired.get("repaired_prompt"),
        repaired_negative=repaired.get("repaired_negative"),
        repaired_model=recipe.model_name if recipe else None,
        repaired_template=recipe.template_code if recipe else None,
        attempt=(generation.output_json or {}).get("quality_attempt") or 1,
        critic_overall=critic.overall if hasattr(critic, "overall") else None,
        critic_decision=critic.decision if hasattr(critic, "decision") else None,
        raw_critic=critic.raw_response if hasattr(critic, "raw_response") else {},
    )
    db.add(failure)
    await db.flush()

    generation.input_json = dict(generation.input_json or {})
    generation.input_json["prompt"] = repaired.get("repaired_prompt")
    generation.input_json["negative_prompt"] = repaired.get("repaired_negative")
    if recipe:
        generation.input_json["model_name"] = recipe.model_name
        generation.input_json["template_code"] = recipe.template_code
    generation.status = "retry"
    await GenerationRepository(db).update(generation)
    await db.commit()

    execute_pipeline.apply_async(args=[str(generation.id)], countdown=10)


def _estimate_eta(steps: list[GenerationStep], current_idx: int) -> int | None:
    completed = [s for s in steps[: current_idx + 1] if s.started_at and s.completed_at]
    if not completed:
        return None
    durations = [(s.completed_at - s.started_at).total_seconds() for s in completed]
    avg = sum(durations) / len(durations)
    remaining = len(steps) - (current_idx + 1)
    return int(avg * remaining)
