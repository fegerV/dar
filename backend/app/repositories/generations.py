from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generation import Generation, GenerationStep, GenerationJob
from app.models.project import Project


class GenerationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, generation_id: UUID) -> Generation | None:
        result = await self.db.execute(select(Generation).where(Generation.id == generation_id))
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Generation], int]:
        query = select(Generation).where(Generation.project_id == project_id)
        count_query = select(func.count()).select_from(Generation).where(
            Generation.project_id == project_id
        )

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = query.order_by(Generation.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, generation: Generation) -> Generation:
        self.db.add(generation)
        await self.db.flush()
        return generation

    async def update(self, generation: Generation) -> Generation:
        await self.db.flush()
        return generation

    async def create_step(self, step: GenerationStep) -> GenerationStep:
        self.db.add(step)
        await self.db.flush()
        return step

    async def update_step(self, step: GenerationStep) -> GenerationStep:
        await self.db.flush()
        return step

    async def get_steps(self, generation_id: UUID) -> list[GenerationStep]:
        result = await self.db.execute(
            select(GenerationStep)
            .where(GenerationStep.generation_id == generation_id)
            .order_by(GenerationStep.step_no.asc())
        )
        return list(result.scalars().all())

    async def create_job(self, job: GenerationJob) -> GenerationJob:
        self.db.add(job)
        await self.db.flush()
        return job

    async def get_latest_for_project(self, project_id: UUID, type_: str | None = None) -> Generation | None:
        query = select(Generation).where(Generation.project_id == project_id)
        if type_:
            query = query.where(Generation.type == type_)
        query = query.order_by(Generation.created_at.desc()).limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
