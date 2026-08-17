"""Seed script: relationship_types, holidays, first templates."""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.template import Scene, Template, TemplateVersion

RELATIONSHIP_TYPES = [
    "parent", "child", "spouse", "partner", "friend",
    "colleague", "boss", "sibling", "grandparent", "grandchild",
]

HOLIDAYS = [
    {"code": "birthday", "title": "День рождения"},
    {"code": "new_year", "title": "Новый год"},
    {"code": "march8", "title": "8 Марта"},
    {"code": "feb23", "title": "23 Февраля"},
    {"code": "wedding_anniversary", "title": "Годовщина свадьбы"},
    {"code": "graduation", "title": "Выпускной"},
    {"code": "mothers_day", "title": "День матери"},
    {"code": "fathers_day", "title": "День отца"},
    {"code": "valentines", "title": "День святого Валентина"},
    {"code": "victory_day", "title": "9 Мая"},
]

FIRST_TEMPLATES = [
    {
        "code": "classic_birthday_warm",
        "title": "Классическое тёплое поздравление",
        "kind": "video",
        "category": "birthday",
        "occasion_codes": ["birthday"],
        "relationship_types": RELATIONSHIP_TYPES,
        "moods": ["warm", "touching"],
        "base_price_rub": 299,
        "estimated_duration_sec": 45,
        "difficulty": 1,
        "personalization_score": 7,
    },
    {
        "code": "funny_friend_roast",
        "title": "Юмористический роаст для друга",
        "kind": "video",
        "category": "birthday",
        "occasion_codes": ["birthday"],
        "relationship_types": ["friend", "colleague", "sibling"],
        "moods": ["funny", "playful"],
        "base_price_rub": 399,
        "estimated_duration_sec": 60,
        "difficulty": 2,
        "personalization_score": 8,
    },
    {
        "code": "new_year_family",
        "title": "Новогоднее семейное поздравление",
        "kind": "video",
        "category": "holiday",
        "occasion_codes": ["new_year"],
        "relationship_types": ["parent", "child", "spouse", "grandparent", "grandchild"],
        "moods": ["festive", "warm"],
        "base_price_rub": 349,
        "estimated_duration_sec": 50,
        "difficulty": 2,
        "personalization_score": 6,
    },
]


async def seed():
    async with async_session_factory() as db:
        # Seed templates
        for tpl_data in FIRST_TEMPLATES:
            existing = await db.execute(
                __import__("sqlalchemy").select(Template).where(Template.code == tpl_data["code"])
            )
            if existing.scalar_one_or_none():
                print(f"Template '{tpl_data['code']}' already exists, skipping")
                continue

            template = Template(**tpl_data, status="published")
            db.add(template)
            await db.flush()

            version = TemplateVersion(
                template_id=template.id,
                version=1,
                status="published",
                schema_version="1.0",
                prompt_config={"system_prompt": "Ты — режиссёр видеопоздравлений.", "temperature": 0.7},
                render_config={"resolution": "1080p", "fps": 30},
                personalization_config={"max_variables": 10},
                validation_config={"min_length_sec": 15, "max_length_sec": 120},
                max_duration_sec=120,
                published_at=datetime.now(timezone.utc),
            )
            db.add(version)
            await db.flush()

            scene = Scene(
                template_id=template.id,
                code="main_scene",
                title="Основная сцена",
                source_type="ai_generated",
                rights_status="cleared",
                duration_sec=tpl_data["estimated_duration_sec"],
                scene_config={"camera": "medium_shot", "lighting": "warm"},
            )
            db.add(scene)
            print(f"Created template: {tpl_data['code']}")

        await db.commit()
        print("Seed completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
