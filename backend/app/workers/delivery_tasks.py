import asyncio
import logging

from celery import shared_task
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.services.scheduler.delivery import DeliveryScheduler

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_scheduled_deliveries(self):
    asyncio.run(_process_scheduled_deliveries())


async def _process_scheduled_deliveries():
    async with async_session() as db:
        scheduler = DeliveryScheduler(db)
        processed = await scheduler.process_due_deliveries()
        logger.info("Processed %d scheduled deliveries", processed)
        return processed
