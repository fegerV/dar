from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.template import Template, TemplateVersion
from app.models.user import User
from app.repositories.recommendations import TemplateRepository
from app.schemas.admin import (
    AdminDashboardStats,
    AdminTemplateCreate,
    AdminTemplateResponse,
    AdminUserResponse,
)


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.template_repo = TemplateRepository(db)

    async def list_users(self, page: int = 1, page_size: int = 20) -> tuple[list[AdminUserResponse], int]:
        count_result = await self.db.execute(select(func.count()).select_from(User))
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(User).order_by(User.created_at.desc()).offset(offset).limit(page_size)
        )
        users = list(result.scalars().all())
        return [AdminUserResponse.model_validate(u) for u in users], total

    async def list_templates(self, page: int = 1, page_size: int = 20) -> tuple[list[AdminTemplateResponse], int]:
        count_result = await self.db.execute(select(func.count()).select_from(Template))
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Template).order_by(Template.created_at.desc()).offset(offset).limit(page_size)
        )
        templates = list(result.scalars().all())
        return [AdminTemplateResponse.model_validate(t) for t in templates], total

    async def create_template(self, body: AdminTemplateCreate) -> AdminTemplateResponse:
        existing = await self.db.execute(
            select(Template).where(Template.code == body.code)
        )
        if existing.scalar_one_or_none():
            raise ConflictException("Template with this code already exists")

        template = Template(
            code=body.code,
            title=body.title,
            description=body.description,
            kind=body.kind,
            status="draft",
            category=body.category,
            occasion_codes=body.occasion_codes,
            relationship_types=body.relationship_types,
            moods=body.moods,
            base_price_rub=body.base_price_rub,
        )
        self.db.add(template)
        await self.db.flush()

        version = TemplateVersion(
            template_id=template.id,
            version=1,
            status="draft",
            schema_version="1.0",
            prompt_config={},
            render_config={},
            personalization_config={},
            validation_config={},
        )
        self.db.add(version)
        await self.db.commit()

        return AdminTemplateResponse.model_validate(template)

    async def get_dashboard_stats(self) -> AdminDashboardStats:
        users_count = await self.db.execute(select(func.count()).select_from(User))
        total_users = users_count.scalar() or 0

        projects_count = await self.db.execute(select(func.count()).select_from(Template))
        total_projects = projects_count.scalar() or 0

        payments_sum = await self.db.execute(
            select(func.coalesce(func.sum(Template.base_price_rub), 0))
        )
        total_payments = float(payments_sum.scalar() or 0)

        pending_reviews = 0
        active_generations = 0

        return AdminDashboardStats(
            total_users=total_users,
            total_projects=total_projects,
            total_payments=total_payments,
            pending_reviews=pending_reviews,
            active_generations=active_generations,
        )
