from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import AnalyticsEvent


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def track_event(
        self,
        event_name: str,
        user_id: UUID | None = None,
        project_id: UUID | None = None,
        session_id: str | None = None,
        properties: dict | None = None,
        platform: str | None = None,
        app_version: str | None = None,
        anonymous_id: str | None = None,
    ) -> None:
        event = AnalyticsEvent(
            user_id=user_id,
            project_id=project_id,
            session_id=session_id,
            event_name=event_name,
            event_version=1,
            platform=platform,
            app_version=app_version,
            anonymous_id=anonymous_id,
            properties=properties or {},
            occurred_at=datetime.now(UTC),
        )
        self.db.add(event)
        await self.db.flush()

    async def track_funnel_event(
        self,
        funnel_name: str,
        step: str,
        user_id: UUID | None = None,
        project_id: UUID | None = None,
        properties: dict | None = None,
    ) -> None:
        await self.track_event(
            event_name=f"funnel_{funnel_name}",
            user_id=user_id,
            project_id=project_id,
            properties={
                "step": step,
                "funnel_name": funnel_name,
                **(properties or {}),
            },
        )

    async def track_nps(self, user_id: UUID, score: int, project_id: UUID | None = None) -> None:
        await self.track_event(
            event_name="nps_survey",
            user_id=user_id,
            project_id=project_id,
            properties={"score": score},
        )

    async def track_csat(self, user_id: UUID, score: int, project_id: UUID | None = None) -> None:
        await self.track_event(
            event_name="csat_survey",
            user_id=user_id,
            project_id=project_id,
            properties={"score": score},
        )
