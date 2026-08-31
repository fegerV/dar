import asyncio
import logging
from datetime import UTC, datetime

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.delivery import Delivery
from app.repositories.delivery import DeliveryRepository
from app.services.delivery.email import EmailDeliveryService
from app.services.delivery.telegram import TelegramDeliveryService

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_scheduled_deliveries(self):
    asyncio.run(_process_scheduled_deliveries())


async def _process_scheduled_deliveries():
    async with async_session() as db:
        repo = DeliveryRepository(db)
        now = datetime.now(UTC)
        result = await db.execute(
            select(Delivery).where(
                Delivery.status == "scheduled",
                Delivery.scheduled_at <= now,
            )
        )
        deliveries = list(result.scalars().all())
        for delivery in deliveries:
            generation = await repo.get_latest_generation(delivery.project_id)
            output = generation.output_json if generation else {}
            video_url = output.get("video_url")
            thumbnail_url = output.get("thumbnail_url")

            if delivery.channel == "email":
                service = EmailDeliveryService(db)
                await service.send(
                    delivery=delivery,
                    video_url=video_url,
                    thumbnail_url=thumbnail_url,
                )
            elif delivery.channel == "telegram":
                service = TelegramDeliveryService(db)
                await service.send(
                    delivery=delivery,
                    video_url=video_url,
                )
            else:
                delivery.status = "sent"
                delivery.sent_at = now
                await db.flush()
                logger.info("Scheduled delivery sent: %s", delivery.id)
        await db.commit()
