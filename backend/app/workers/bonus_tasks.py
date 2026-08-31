import asyncio
import logging
from datetime import UTC, datetime, timedelta

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.payment import Entitlement
from app.repositories.entitlements import EntitlementRepository

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def friday_bonus(self):
    asyncio.run(_friday_bonus())


async def _friday_bonus():
    async with async_session() as db:
        repo = EntitlementRepository(db)
        stmt = (
            select(Entitlement.user_id)
            .where(Entitlement.code == "friday_bonus")
            .group_by(Entitlement.user_id)
        )
        result = await db.execute(stmt)
        users = [row[0] for row in result.all()]
        for user_id in users:
            entitlement = Entitlement(
                user_id=user_id,
                code="bonus_balance",
                quantity=30,
                consumed=0,
                source="friday_bonus",
                expires_at=datetime.now(UTC) + timedelta(days=7),
                created_at=datetime.now(UTC),
            )
            await repo.create(entitlement)
        await db.commit()
        logger.info("Friday bonus granted to %s users", len(users))
