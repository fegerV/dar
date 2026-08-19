from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Entitlement
from app.models.project import Project
from app.models.template import Template, TemplateVersion


class PricingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_template(self, template_id: UUID) -> Template | None:
        result = await self.db.execute(select(Template).where(Template.id == template_id))
        return result.scalar_one_or_none()

    async def get_template_version(self, version_id: UUID) -> TemplateVersion | None:
        result = await self.db.execute(select(TemplateVersion).where(TemplateVersion.id == version_id))
        return result.scalar_one_or_none()

    async def get_project(self, project_id: UUID) -> Project | None:
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()

    async def get_entitlement_by_code(self, user_id: UUID, code: str) -> Entitlement | None:
        result = await self.db.execute(
            select(Entitlement).where(
                Entitlement.user_id == user_id,
                Entitlement.code == code,
                Entitlement.consumed < Entitlement.quantity,
            )
        )
        return result.scalar_one_or_none()

    async def update_project(self, project: Project) -> Project:
        await self.db.flush()
        return project
