import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lab import LabBenchmark, LabPhoto, LabRecipeProposal, LabScenario
from app.schemas.lab import (
    LabBenchmarkCreate,
    LabBenchmarkResultUpdate,
    LabRecipeProposalApprove,
    LabStatsResponse,
    LabScenarioCreate,
)


class LabService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_scenarios(self, active_only: bool = True) -> list[LabScenario]:
        stmt = select(LabScenario)
        if active_only:
            stmt = stmt.where(LabScenario.is_active == 1)
        stmt = stmt.order_by(LabScenario.code)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_scenario(self, scenario_id: uuid.UUID) -> LabScenario | None:
        stmt = select(LabScenario).where(LabScenario.id == scenario_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_scenario(self, data: LabScenarioCreate) -> LabScenario:
        scenario = LabScenario(
            code=data.code,
            name=data.name,
            description=data.description,
            category=data.category,
            difficulty=data.difficulty,
            prompt_template=data.prompt_template,
            negative_strategy=data.negative_strategy,
            target_duration_sec=data.target_duration_sec,
            target_camera=data.target_camera,
            target_motion=data.target_motion,
            tags=data.tags,
            meta=data.meta,
            is_active=data.is_active,
        )
        self.db.add(scenario)
        await self.db.flush()
        await self.db.refresh(scenario)
        return scenario

    async def list_photos(self, scenario_code: str | None = None) -> list[LabPhoto]:
        stmt = select(LabPhoto)
        if scenario_code:
            stmt = stmt.where(LabPhoto.scenario_code == scenario_code)
        stmt = stmt.order_by(LabPhoto.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_photo(
        self,
        filename: str,
        file_url: str,
        scenario_code: str | None = None,
        original_name: str | None = None,
        file_size_bytes: int | None = None,
        mime_type: str | None = None,
        width: int | None = None,
        height: int | None = None,
        metadata: dict | None = None,
    ) -> LabPhoto:
        photo = LabPhoto(
            scenario_code=scenario_code,
            filename=filename,
            original_name=original_name,
            file_url=file_url,
            file_size_bytes=file_size_bytes,
            mime_type=mime_type,
            width=width,
            height=height,
            metadata=metadata or {},
        )
        self.db.add(photo)
        await self.db.flush()
        await self.db.refresh(photo)
        return photo

    async def list_benchmarks(
        self,
        scenario_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> list[LabBenchmark]:
        stmt = select(LabBenchmark).options(
            selectinload(LabBenchmark.scenario),
            selectinload(LabBenchmark.photo),
        )
        if scenario_id:
            stmt = stmt.where(LabBenchmark.scenario_id == scenario_id)
        if status:
            stmt = stmt.where(LabBenchmark.status == status)
        stmt = stmt.order_by(LabBenchmark.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_benchmark(self, benchmark_id: uuid.UUID) -> LabBenchmark | None:
        stmt = (
            select(LabBenchmark)
            .options(
                selectinload(LabBenchmark.scenario),
                selectinload(LabBenchmark.photo),
            )
            .where(LabBenchmark.id == benchmark_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_benchmark(self, data: LabBenchmarkCreate) -> LabBenchmark:
        benchmark = LabBenchmark(
            scenario_id=data.scenario_id,
            photo_id=data.photo_id,
            model_name=data.model_name,
            model_version=data.model_version,
            cost_estimate=data.cost_estimate,
            status="draft",
        )
        self.db.add(benchmark)
        await self.db.flush()
        await self.db.refresh(benchmark)
        return benchmark

    async def update_benchmark_result(
        self, benchmark_id: uuid.UUID, data: LabBenchmarkResultUpdate
    ) -> LabBenchmark | None:
        benchmark = await self.get_benchmark(benchmark_id)
        if not benchmark:
            return None
        update_data = data.model_dump(exclude_unset=True)
        if "status" in update_data:
            new_status = update_data["status"]
            if new_status == "running" and not benchmark.started_at:
                benchmark.started_at = datetime.now(timezone.utc)
            elif new_status in ("completed", "failed"):
                benchmark.completed_at = datetime.now(timezone.utc)
                if "status" not in update_data or update_data["status"] == "completed":
                    benchmark.status = new_status
                else:
                    benchmark.status = new_status
        for field, value in update_data.items():
            if field != "status":
                setattr(benchmark, field, value)
        await self.db.flush()
        await self.db.refresh(benchmark)
        return benchmark

    async def create_recipe_proposal(
        self,
        benchmark_id: uuid.UUID,
        recipe_code: str,
        recipe_name: str,
        template_code: str,
        model_name: str,
        confidence_score: float | None = None,
    ) -> LabRecipeProposal:
        proposal = LabRecipeProposal(
            benchmark_id=benchmark_id,
            recipe_code=recipe_code,
            recipe_name=recipe_name,
            template_code=template_code,
            model_name=model_name,
            confidence_score=confidence_score,
            auto_generated=True,
        )
        self.db.add(proposal)
        await self.db.flush()
        await self.db.refresh(proposal)
        return proposal

    async def approve_recipe_proposal(
        self,
        proposal_id: uuid.UUID,
        data: LabRecipeProposalApprove,
        approved_by: str | None = None,
    ) -> LabRecipeProposal | None:
        stmt = select(LabRecipeProposal).where(LabRecipeProposal.id == proposal_id)
        result = await self.db.execute(stmt)
        proposal = result.scalar_one_or_none()
        if not proposal:
            return None
        proposal.approved = data.approved
        if data.approved:
            proposal.approved_by = approved_by
            proposal.approved_at = datetime.now(timezone.utc)
            if data.recipe_name:
                proposal.recipe_name = data.recipe_name
            if data.confidence_score is not None:
                proposal.confidence_score = data.confidence_score
        await self.db.flush()
        await self.db.refresh(proposal)
        return proposal

    async def apply_proposal_to_production(self, proposal_id: uuid.UUID) -> bool:
        stmt = select(LabRecipeProposal).where(LabRecipeProposal.id == proposal_id)
        result = await self.db.execute(stmt)
        proposal = result.scalar_one_or_none()
        if not proposal or not proposal.approved:
            return False
        from app.models.intelligence import VideoRecipe

        existing_stmt = select(VideoRecipe).where(VideoRecipe.code == proposal.recipe_code)
        existing_result = await self.db.execute(existing_stmt)
        existing = existing_result.scalar_one_or_none()
        if existing:
            existing.name = proposal.recipe_name
            existing.template_code = proposal.template_code
            existing.model_name = proposal.model_name
            existing.is_active = True
        else:
            recipe = VideoRecipe(
                code=proposal.recipe_code,
                name=proposal.recipe_name,
                template_code=proposal.template_code,
                model_name=proposal.model_name,
                is_active=True,
            )
            self.db.add(recipe)
        proposal.applied_to_production = True
        await self.db.flush()
        return True

    async def get_stats(self) -> LabStatsResponse:
        total_scenarios = await self.db.scalar(select(func.count(LabScenario.id)))
        total_photos = await self.db.scalar(select(func.count(LabPhoto.id)))
        total_benchmarks = await self.db.scalar(select(func.count(LabBenchmark.id)))
        completed = await self.db.scalar(
            select(func.count(LabBenchmark.id)).where(LabBenchmark.status == "completed")
        )
        failed = await self.db.scalar(
            select(func.count(LabBenchmark.id)).where(LabBenchmark.status == "failed")
        )
        avg_quality = await self.db.scalar(
            select(func.avg(LabBenchmark.quality_score)).where(LabBenchmark.status == "completed")
        )
        avg_success = await self.db.scalar(
            select(func.avg(LabBenchmark.success_rate)).where(LabBenchmark.status == "completed")
        )
        avg_cost = await self.db.scalar(
            select(func.avg(LabBenchmark.actual_cost)).where(LabBenchmark.status == "completed")
        )
        proposals_approved = await self.db.scalar(
            select(func.count(LabRecipeProposal.id)).where(LabRecipeProposal.approved == 1)
        )
        proposals_applied = await self.db.scalar(
            select(func.count(LabRecipeProposal.id)).where(LabRecipeProposal.applied_to_production == 1)
        )
        return LabStatsResponse(
            total_scenarios=total_scenarios or 0,
            total_photos=total_photos or 0,
            total_benchmarks=total_benchmarks or 0,
            completed_benchmarks=completed or 0,
            failed_benchmarks=failed or 0,
            avg_quality_score=float(avg_quality) if avg_quality else None,
            avg_success_rate=float(avg_success) if avg_success else None,
            avg_cost=float(avg_cost) if avg_cost else None,
            proposals_approved=proposals_approved or 0,
            proposals_applied=proposals_applied or 0,
        )
