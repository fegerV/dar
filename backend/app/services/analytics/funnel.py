from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import AnalyticsEvent
from app.models.project import Project
from app.models.user import User
from app.repositories.projects import ProjectRepository
from app.services.analytics.service import AnalyticsService


class FunnelService:
    FUNNEL_STEPS = [
        "visit",
        "register",
        "create_project",
        "complete_brief",
        "select_template",
        "pay",
        "deliver",
    ]

    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics = AnalyticsService(db)
        self.project_repo = ProjectRepository(db)

    async def track_step(self, funnel_name: str, step: str, user_id: UUID | None = None, project_id: UUID | None = None) -> None:
        await self.analytics.track_funnel_event(funnel_name, step, user_id, project_id)

    async def get_funnel_stats(self, funnel_name: str, days: int = 7) -> dict:
        result = await self.db.execute(
            select(
                AnalyticsEvent.properties["step"].astext.label("step"),
                func.count().label("count"),
            )
            .where(
                AnalyticsEvent.event_name == f"funnel_{funnel_name}",
                AnalyticsEvent.occurred_at >= func.now() - func.cast(f"{days} days", func.interval()),
            )
            .group_by(AnalyticsEvent.properties["step"].astext)
            .order_by(AnalyticsEvent.properties["step"].astext)
        )
        rows = result.all()
        stats = {step: 0 for step in self.FUNNEL_STEPS}
        for row in rows:
            stats[row.step] = row.count
        return stats

    async def get_conversion_rates(self, funnel_name: str, days: int = 7) -> dict:
        stats = await self.get_funnel_stats(funnel_name, days)
        rates = {}
        total = stats.get("visit", 0)
        if total > 0:
            for step in self.FUNNEL_STEPS:
                rates[step] = round((stats.get(step, 0) / total) * 100, 2)
        return rates

    async def get_drop_off_analysis(self, funnel_name: str, days: int = 7) -> dict:
        stats = await self.get_funnel_stats(funnel_name, days)
        drop_offs = {}
        for i, step in enumerate(self.FUNNEL_STEPS):
            if i == 0:
                continue
            prev_step = self.FUNNEL_STEPS[i - 1]
            prev_count = stats.get(prev_step, 0)
            curr_count = stats.get(step, 0)
            if prev_count > 0:
                drop_offs[step] = round(((prev_count - curr_count) / prev_count) * 100, 2)
            else:
                drop_offs[step] = 0.0
        return drop_offs
