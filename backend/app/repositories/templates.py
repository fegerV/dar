from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.template import Template, TemplateVersion


class TemplateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_version(self, version_id: UUID) -> TemplateVersion | None:
        result = await self.db.execute(select(TemplateVersion).where(TemplateVersion.id == version_id))
        return result.scalar_one_or_none()

    async def list_versions(self, template_id: int) -> list[TemplateVersion]:
        result = await self.db.execute(
            select(TemplateVersion).where(TemplateVersion.template_id == template_id)
        )
        return list(result.scalars().all())
