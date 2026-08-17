from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recommendation import Recommendation
from app.models.template import Template, TemplateVersion


class RecommendationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_project(
        self,
        project_id: UUID,
        status: str | None = None,
    ) -> list[Recommendation]:
        query = select(Recommendation).where(Recommendation.project_id == project_id)
        if status:
            query = query.where(Recommendation.status == status)
        query = query.order_by(Recommendation.rank.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, recommendation_id: UUID, project_id: UUID) -> Recommendation | None:
        result = await self.db.execute(
            select(Recommendation).where(
                Recommendation.id == recommendation_id,
                Recommendation.project_id == project_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, recommendation: Recommendation) -> Recommendation:
        self.db.add(recommendation)
        await self.db.flush()
        return recommendation

    async def bulk_create(self, recommendations: list[Recommendation]) -> None:
        self.db.add_all(recommendations)
        await self.db.flush()

    async def mark_selected(
        self, recommendation_id: UUID, project_id: UUID, template_version_id: UUID
    ) -> Recommendation | None:
        rec = await self.get_by_id(recommendation_id, project_id)
        if rec:
            rec.status = "selected"
            rec.selected_at = datetime.now(datetime.timezone.utc)
        return rec


class TemplateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_active(
        self,
        occasion_codes: list[str] | None = None,
        relationship_types: list[str] | None = None,
        moods: list[str] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Template], int]:
        query = select(Template).where(Template.status == "published")
        count_query = select(func.count()).select_from(Template).where(Template.status == "published")

        if occasion_codes:
            query = query.where(Template.occasion_codes.contains(occasion_codes))
            count_query = count_query.where(Template.occasion_codes.contains(occasion_codes))

        if relationship_types:
            query = query.where(Template.relationship_types.contains(relationship_types))
            count_query = count_query.where(Template.relationship_types.contains(relationship_types))

        if moods:
            query = query.where(Template.moods.contains(moods))
            count_query = count_query.where(Template.moods.contains(moods))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = query.order_by(Template.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_id(self, template_id: UUID) -> Template | None:
        result = await self.db.execute(select(Template).where(Template.id == template_id))
        return result.scalar_one_or_none()

    async def get_version(self, template_id: UUID, version: int) -> TemplateVersion | None:
        result = await self.db.execute(
            select(TemplateVersion).where(
                TemplateVersion.template_id == template_id,
                TemplateVersion.version == version,
            )
        )
        return result.scalar_one_or_none()

    async def get_latest_version(self, template_id: UUID) -> TemplateVersion | None:
        result = await self.db.execute(
            select(TemplateVersion)
            .where(TemplateVersion.template_id == template_id)
            .order_by(TemplateVersion.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
