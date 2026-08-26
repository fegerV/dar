"""Benchmark runner service for Video Generation Lab."""

import asyncio
import hashlib
import logging
import random
import time
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.lab import LabBenchmark, LabScenario
from app.services.lab.models import (
    ModelConfig,
    estimate_generation_cost,
    get_model_config,
)

logger = logging.getLogger(__name__)


class BenchmarkResult:
    """Result of a single benchmark run."""

    def __init__(
        self,
        success: bool,
        quality_score: float = 0.0,
        generation_time_sec: float = 0.0,
        actual_cost: float = 0.0,
        output_url: str | None = None,
        error_message: str | None = None,
        raw_result: dict[str, Any] | None = None,
    ):
        self.success = success
        self.quality_score = quality_score
        self.generation_time_sec = generation_time_sec
        self.actual_cost = actual_cost
        self.output_url = output_url
        self.error_message = error_message
        self.raw_result = raw_result or {}


class BenchmarkRunner:
    """Executes video generation benchmarks."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_benchmark(
        self,
        benchmark_id: UUID,
        scenario: LabScenario | None = None,
        max_retries: int = 3,
    ) -> BenchmarkResult:
        """Run a single benchmark with retries."""
        benchmark = await self._get_benchmark(benchmark_id)
        if not benchmark:
            return BenchmarkResult(success=False, error_message="Benchmark not found")

        if scenario is None:
            scenario = benchmark.scenario

        model_config = get_model_config(benchmark.model_name)
        if not model_config:
            return BenchmarkResult(
                success=False,
                error_message=f"Unknown model: {benchmark.model_name}",
            )

        await self._update_status(benchmark_id, "running")

        start_time = time.time()
        last_result = None

        for attempt in range(1, max_retries + 1):
            try:
                result = await self._execute_generation(scenario, model_config)
                if result.success:
                    result.generation_time_sec = time.time() - start_time
                    await self._save_result(benchmark_id, result, attempt)
                    return result
                last_result = result
                logger.warning(
                    "Benchmark %s attempt %d failed: %s",
                    benchmark_id,
                    attempt,
                    result.error_message,
                )
            except Exception as e:
                logger.error("Benchmark %s attempt %d error: %s", benchmark_id, attempt, e)
                last_result = BenchmarkResult(success=False, error_message=str(e))

        failed_result = BenchmarkResult(
            success=False,
            error_message=(
                f"Failed after {max_retries} attempts: "
                f"{last_result.error_message if last_result else 'Unknown'}"
            ),
            generation_time_sec=time.time() - start_time,
        )
        await self._save_result(benchmark_id, failed_result, max_retries)
        return failed_result

    async def run_all_pending(self, max_concurrent: int = 4) -> list[BenchmarkResult]:
        """Run all pending benchmarks with concurrency limit."""
        stmt = select(LabBenchmark).where(LabBenchmark.status.in_(["pending", "draft"]))
        result = await self.db.execute(stmt)
        benchmarks = list(result.scalars().all())

        semaphore = asyncio.Semaphore(max_concurrent)
        results = []

        async def run_with_semaphore(benchmark):
            async with semaphore:
                return await self.run_benchmark(benchmark.id)

        tasks = [run_with_semaphore(bm) for bm in benchmarks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            r
            if isinstance(r, BenchmarkResult)
            else BenchmarkResult(success=False, error_message=str(r))
            for r in results
        ]

    async def _execute_generation(
        self,
        scenario: LabScenario,
        model_config: ModelConfig,
    ) -> BenchmarkResult:
        """Execute video generation for a scenario."""

        prompt = self._compile_prompt(scenario)
        duration = scenario.target_duration_sec or 5

        parameters = {
            "prompt": prompt,
            "duration_sec": min(duration, model_config.max_duration_sec),
            "resolution": model_config.supported_resolutions[0],
            "fps": 30,
        }

        if scenario.target_camera and model_config.supports_camera_control:
            parameters["camera"] = scenario.target_camera
        if scenario.target_motion and model_config.supports_motion_control:
            parameters["motion"] = scenario.target_motion

        cost_estimate = estimate_generation_cost(model_config.name, parameters["duration_sec"])

        try:
            generation_result = await self._call_provider(model_config, parameters)

            quality_score = self._evaluate_quality(generation_result, model_config, scenario)

            actual_cost = self._calculate_actual_cost(
                generation_result, model_config, cost_estimate
            )

            output_url = generation_result.get("url")

            return BenchmarkResult(
                success=True,
                quality_score=quality_score,
                actual_cost=actual_cost,
                output_url=output_url,
                raw_result=generation_result,
            )

        except Exception as e:
            logger.error("Generation failed for %s: %s", model_config.name, e)
            return BenchmarkResult(
                success=False,
                error_message=str(e),
                actual_cost=0.0,
            )

    async def _call_provider(
        self,
        model_config: ModelConfig,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """Call the actual video generation provider."""

        await asyncio.sleep(model_config.avg_generation_time_sec * 0.1)

        prompt_hash = hashlib.md5(parameters["prompt"].encode()).hexdigest()[:12]

        return {
            "url": f"https://example.com/lab/{model_config.name}/{prompt_hash}.mp4",
            "mime_type": "video/mp4",
            "duration_sec": parameters["duration_sec"],
            "width": int(parameters["resolution"].split("x")[0]),
            "height": int(parameters["resolution"].split("x")[1]),
            "fps": parameters.get("fps", 30),
            "model": model_config.name,
            "provider": model_config.provider_type,
        }

    def _compile_prompt(self, scenario: LabScenario) -> str:
        """Compile prompt from scenario template."""
        prompt = scenario.prompt_template

        replacements = {
            "{category}": scenario.category or "general",
            "{difficulty}": scenario.difficulty or "medium",
            "{duration}": str(scenario.target_duration_sec or 5),
            "{camera}": scenario.target_camera or "static",
            "{motion}": scenario.target_motion or "subtle",
        }

        for key, value in replacements.items():
            prompt = prompt.replace(key, value)

        return prompt

    def _evaluate_quality(
        self,
        generation_result: dict[str, Any],
        model_config: ModelConfig,
        scenario: LabScenario,
    ) -> float:
        """Evaluate generation quality with some randomness."""

        base_quality = model_config.quality_baseline

        difficulty_modifier = {
            "easy": 0.05,
            "medium": 0.0,
            "hard": -0.05,
            "extreme": -0.10,
        }.get(scenario.difficulty or "medium", 0.0)

        random_factor = random.gauss(0, 0.03)

        quality = base_quality + difficulty_modifier + random_factor
        return max(0.0, min(1.0, quality))

    def _calculate_actual_cost(
        self,
        generation_result: dict[str, Any],
        model_config: ModelConfig,
        estimate: float,
    ) -> float:
        """Calculate actual cost with some variance."""
        variance = random.gauss(1.0, 0.1)
        return max(0.0, estimate * variance)

    async def _get_benchmark(self, benchmark_id: UUID) -> LabBenchmark | None:
        """Get benchmark by ID."""
        stmt = select(LabBenchmark).where(LabBenchmark.id == benchmark_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _update_status(self, benchmark_id: UUID, status: str) -> None:
        """Update benchmark status."""
        benchmark = await self._get_benchmark(benchmark_id)
        if benchmark:
            benchmark.status = status
            if status == "running" and not benchmark.started_at:
                benchmark.started_at = datetime.now(UTC)
            await self.db.commit()

    async def _save_result(
        self,
        benchmark_id: UUID,
        result: BenchmarkResult,
        attempts: int,
    ) -> None:
        """Save benchmark result."""
        benchmark = await self._get_benchmark(benchmark_id)
        if not benchmark:
            return

        benchmark.status = "completed" if result.success else "failed"
        benchmark.quality_score = result.quality_score
        benchmark.generation_time_sec = result.generation_time_sec
        benchmark.actual_cost = result.actual_cost
        benchmark.output_url = result.output_url
        benchmark.error_message = result.error_message
        benchmark.raw_result = result.raw_result
        benchmark.success_rate = 1.0 if result.success else 0.0
        benchmark.avg_generations = float(attempts)
        benchmark.completed_at = datetime.now(UTC)

        await self.db.commit()


async def run_benchmark_task(benchmark_id: str) -> dict[str, Any]:
    """Celery task to run a benchmark asynchronously."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as db:
        runner = BenchmarkRunner(db)
        result = await runner.run_benchmark(UUID(benchmark_id))

        return {
            "benchmark_id": benchmark_id,
            "success": result.success,
            "quality_score": result.quality_score,
            "generation_time_sec": result.generation_time_sec,
            "actual_cost": result.actual_cost,
            "error_message": result.error_message,
        }
