from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generation import Generation


class QualityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_generation(self, generation_id: UUID) -> Generation | None:
        result = await self.db.execute(
            select(Generation).where(Generation.id == generation_id)
        )
        return result.scalar_one_or_none()

    async def update_generation_status(
        self, generation_id: UUID, status: str, output_json: dict | None = None
    ) -> Generation | None:
        generation = await self.get_generation(generation_id)
        if generation is None:
            return None
        generation.status = status
        if output_json:
            generation.output_json = output_json
        generation.completed_at = datetime.now(datetime.timezone.utc)
        await self.db.flush()
        return generation
