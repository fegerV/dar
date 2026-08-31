import random
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import AnalyticsEvent
from app.services.analytics.service import AnalyticsService


class FeatureFlagService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics = AnalyticsService(db)

    async def is_enabled(self, user_id: UUID, flag_name: str, default: bool = False) -> bool:
        result = await self.db.execute(
            select(AnalyticsEvent)
            .where(
                AnalyticsEvent.event_name == "feature_flag",
                AnalyticsEvent.user_id == user_id,
                AnalyticsEvent.properties["flag_name"].astext == flag_name,
            )
            .order_by(AnalyticsEvent.occurred_at.desc())
            .limit(1)
        )
        event = result.scalar_one_or_none()
        if event:
            return event.properties.get("enabled", default)
        return default

    async def set_flag(self, user_id: UUID, flag_name: str, enabled: bool) -> None:
        await self.analytics.track_event(
            event_name="feature_flag",
            user_id=user_id,
            properties={"flag_name": flag_name, "enabled": enabled},
        )


class ABTestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics = AnalyticsService(db)

    async def get_variant(self, user_id: UUID, test_name: str, variants: list[str]) -> str:
        result = await self.db.execute(
            select(AnalyticsEvent)
            .where(
                AnalyticsEvent.event_name == "ab_test_assignment",
                AnalyticsEvent.user_id == user_id,
                AnalyticsEvent.properties["test_name"].astext == test_name,
            )
            .order_by(AnalyticsEvent.occurred_at.desc())
            .limit(1)
        )
        event = result.scalar_one_or_none()
        if event:
            return event.properties.get("variant", variants[0])

        variant = random.choice(variants)
        await self.analytics.track_event(
            event_name="ab_test_assignment",
            user_id=user_id,
            properties={"test_name": test_name, "variant": variant},
        )
        return variant

    async def track_conversion(self, user_id: UUID, test_name: str, variant: str, conversion: bool) -> None:
        await self.analytics.track_event(
            event_name="ab_test_conversion",
            user_id=user_id,
            properties={
                "test_name": test_name,
                "variant": variant,
                "conversion": conversion,
            },
        )
