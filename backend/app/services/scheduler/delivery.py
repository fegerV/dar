import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery import Delivery

logger = logging.getLogger(__name__)


class DeliveryScheduler:
    BATCH_SIZE = 100
    POLL_INTERVAL_SECONDS = 60
    WORKER_TIMEOUT_SECONDS = 300

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_due_deliveries(self, limit: int | None = None) -> int:
        batch_size = limit or self.BATCH_SIZE
        now = datetime.now(UTC)

        due_deliveries = await self.db.execute(
            select(Delivery)
            .where(
                Delivery.status == "scheduled",
                Delivery.scheduled_at <= now,
                Delivery.scheduled_at.is_not(None),
            )
            .limit(batch_size)
        )
        deliveries = list(due_deliveries.scalars().all())

        processed = 0
        for delivery in deliveries:
            try:
                await self._execute_delivery(delivery)
                processed += 1
            except Exception as e:
                logger.error("Failed to process scheduled delivery %s: %s", delivery.id, e)
                delivery.status = "failed"
                delivery.error_message = str(e)
                delivery.failed_at = now

        await self.db.commit()
        return processed

    async def _execute_delivery(self, delivery: Delivery) -> None:
        if delivery.channel == "email":
            from app.services.delivery.email import EmailDeliveryService

            service = EmailDeliveryService(self.db)
            generation_result = await self._get_generation_output(delivery)
            await service.send(
                delivery=delivery,
                video_url=generation_result.get("video_url"),
                thumbnail_url=generation_result.get("thumbnail_url"),
            )
        elif delivery.channel == "telegram":
            from app.services.delivery.telegram import TelegramDeliveryService

            service = TelegramDeliveryService(self.db)
            generation_result = await self._get_generation_output(delivery)
            await service.send(
                delivery=delivery,
                video_url=generation_result.get("video_url"),
            )

    async def _get_generation_output(self, delivery: Delivery) -> dict:
        if delivery.generation_id is None:
            return {}
        from app.repositories.generations import GenerationRepository

        gen_repo = GenerationRepository(self.db)
        generation = await gen_repo.get_by_id(delivery.generation_id)
        if generation and generation.output_json:
            return generation.output_json
        return {}

    async def schedule_delivery_with_timezone(
        self,
        project_id: UUID,
        channel: str,
        destination: str | None,
        scheduled_at: datetime,
        user_timezone: str = "UTC",
    ) -> Delivery:
        utc_scheduled = scheduled_at
        if scheduled_at.tzinfo is None:
            from zoneinfo import ZoneInfo

            try:
                tz = ZoneInfo(user_timezone)
                utc_scheduled = scheduled_at.replace(tzinfo=tz).astimezone(UTC)
            except Exception:
                utc_scheduled = scheduled_at.replace(tzinfo=UTC)

        delivery = Delivery(
            project_id=project_id,
            channel=channel,
            status="scheduled",
            destination=destination,
            scheduled_at=utc_scheduled,
        )
        self.db.add(delivery)
        await self.db.flush()
        return delivery

    async def get_pending_count(self) -> int:
        now = datetime.now(UTC)
        result = await self.db.execute(
            select(Delivery)
            .where(
                Delivery.status == "scheduled",
                Delivery.scheduled_at <= now,
            )
        )
        return len(result.scalars().all())
