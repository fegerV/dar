"""Seed script for Video Generation Lab scenarios."""

import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.lab import LabScenario
from app.services.lab.seed_data import get_scenario_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_scenarios():
    """Seed lab scenarios if they don't exist."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as db:
        scenario_data = get_scenario_data()
        created_count = 0

        for data in scenario_data:
            stmt = select(LabScenario).where(LabScenario.code == data["code"])
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                logger.info("Scenario %s already exists, skipping", data["code"])
                continue

            scenario = LabScenario(
                code=data["code"],
                name=data["name"],
                description=data["description"],
                category=data["category"],
                difficulty=data["difficulty"],
                prompt_template=data["prompt_template"],
                negative_strategy=data["negative_strategy"],
                target_duration_sec=data["target_duration_sec"],
                target_camera=data["target_camera"],
                target_motion=data["target_motion"],
                tags=data["tags"],
                is_active=1,
            )
            db.add(scenario)
            created_count += 1
            logger.info("Created scenario: %s", data["code"])

        await db.commit()
        logger.info("Seeded %d new scenarios (total: %d)", created_count, len(scenario_data)))

        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_scenarios())
