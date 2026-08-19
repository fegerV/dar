from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Entitlement, PromoCode
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

    async def get_promo_code(self, code: str) -> PromoCode | None:
        result = await self.db.execute(
            select(PromoCode).where(
                PromoCode.code == code,
                PromoCode.is_active.is_(True),
            )
        )
        promo = result.scalar_one_or_none()
        if promo is None:
            return None
        if promo.expires_at and promo.expires_at < datetime.now(UTC):
            return None
        if promo.max_uses is not None and promo.used_count >= promo.max_uses:
            return None
        return promo

    async def increment_promo_usage(self, promo_id: UUID, max_uses: int | None = None) -> bool:
        stmt = sa_update(PromoCode).where(PromoCode.id == promo_id)
        if max_uses is not None:
            stmt = stmt.where(PromoCode.used_count < max_uses)
        stmt = stmt.values(used_count=PromoCode.used_count + 1).returning(PromoCode.id)
        result = await self.db.execute(stmt)
        return result.one_or_none() is not None
