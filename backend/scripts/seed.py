"""Seed script: relationship_types, holidays, first templates."""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.holiday import Holiday
from app.models.relationship import RelationshipType
from app.models.template import Scene, Template, TemplateVersion

RELATIONSHIP_TYPES = [
    "parent", "child", "spouse", "partner", "friend",
    "colleague", "boss", "sibling", "grandparent", "grandchild",
    "classmate", "teacher", "relative",
]

HOLIDAYS = [
    {"code": "birthday", "title": "День рождения", "kind": "personal"},
    {"code": "new_year", "title": "Новый год", "kind": "state", "month": 1, "day": 1, "country_code": "RU"},
    {"code": "christmas", "title": "Рождество Христово", "kind": "state", "month": 1, "day": 7, "country_code": "RU"},
    {"code": "feb23", "title": "23 февраля", "kind": "state", "month": 2, "day": 23, "country_code": "RU"},
    {"code": "march8", "title": "8 марта", "kind": "state", "month": 3, "day": 8, "country_code": "RU"},
    {"code": "may1", "title": "Праздник Весны и Труда", "kind": "state", "month": 5, "day": 1, "country_code": "RU"},
    {"code": "victory_day", "title": "9 мая", "kind": "state", "month": 5, "day": 9, "country_code": "RU"},
    {"code": "russia_day", "title": "День России", "kind": "state", "month": 6, "day": 12, "country_code": "RU"},
    {"code": "unity_day", "title": "День народного единства", "kind": "state", "month": 11, "day": 4, "country_code": "RU"},
    {"code": "programmer_day", "title": "День программиста", "kind": "professional", "month": 9, "day": 13, "country_code": "RU"},
    {"code": "teacher_day", "title": "День учителя", "kind": "professional", "month": 10, "day": 5, "country_code": "RU"},
    {"code": "builder_day", "title": "День строителя", "kind": "professional", "month": 8, "day": 11, "country_code": "RU"},
    {"code": "doctor_day", "title": "День врача", "kind": "professional", "month": 6, "day": 19, "country_code": "RU"},
    {"code": "valentines", "title": "День святого Валентина", "kind": "thematic", "month": 2, "day": 14, "country_code": "RU"},
    {"code": "halloween", "title": "Хэллоуин", "kind": "thematic", "month": 10, "day": 31, "country_code": "RU"},
]

FIRST_TEMPLATES = [
    {"code": "classic_birthday_warm", "title": "Классическое тёплое поздравление", "kind": "video", "category": "birthday", "occasion_codes": ["birthday"], "relationship_types": RELATIONSHIP_TYPES, "moods": ["warm", "touching"], "base_price_rub": 299, "estimated_duration_sec": 45, "difficulty": 1, "personalization_score": 7},
    {"code": "funny_friend_roast", "title": "Юмористический роаст для друга", "kind": "video", "category": "birthday", "occasion_codes": ["birthday"], "relationship_types": ["friend", "colleague", "sibling"], "moods": ["funny", "playful"], "base_price_rub": 399, "estimated_duration_sec": 60, "difficulty": 2, "personalization_score": 8},
    {"code": "new_year_family", "title": "Новогоднее семейное поздравление", "kind": "video", "category": "holiday", "occasion_codes": ["new_year"], "relationship_types": ["parent", "child", "spouse", "grandparent", "grandchild"], "moods": ["festive", "warm"], "base_price_rub": 349, "estimated_duration_sec": 50, "difficulty": 2, "personalization_score": 6},
    {"code": "space_captain_birthday", "title": "Космический капитан", "kind": "video", "category": "cinematic", "occasion_codes": ["birthday", "anniversary"], "relationship_types": ["parent", "spouse", "partner"], "moods": ["epic", "warm"], "base_price_rub": 699, "estimated_duration_sec": 60, "difficulty": 3, "personalization_score": 9},
    {"code": "secret_agent_birthday", "title": "Секретная операция", "kind": "video", "category": "cinematic", "occasion_codes": ["birthday"], "relationship_types": ["friend", "colleague", "classmate"], "moods": ["funny", "brutal"], "base_price_rub": 699, "estimated_duration_sec": 50, "difficulty": 3, "personalization_score": 9},
    {"code": "hollywood_trailer", "title": "Голливудский трейлер", "kind": "video", "category": "cinematic", "occasion_codes": ["birthday", "anniversary"], "relationship_types": RELATIONSHIP_TYPES, "moods": ["epic", "official"], "base_price_rub": 799, "estimated_duration_sec": 60, "difficulty": 3, "personalization_score": 8},
    {"code": "news_future", "title": "Новости будущего", "kind": "video", "category": "cinematic", "occasion_codes": ["birthday", "new_year"], "relationship_types": ["friend", "colleague", "sibling"], "moods": ["funny", "surprising"], "base_price_rub": 599, "estimated_duration_sec": 45, "difficulty": 2, "personalization_score": 7},
    {"code": "court_trial", "title": "Суд над именинником", "kind": "video", "category": "humor", "occasion_codes": ["birthday"], "relationship_types": ["friend", "colleague", "classmate"], "moods": ["funny", "ironic"], "base_price_rub": 599, "estimated_duration_sec": 50, "difficulty": 2, "personalization_score": 8},
    {"code": "interview_star", "title": "Интервью со звездой", "kind": "video", "category": "humor", "occasion_codes": ["birthday", "anniversary"], "relationship_types": ["spouse", "partner", "friend"], "moods": ["funny", "romantic"], "base_price_rub": 699, "estimated_duration_sec": 55, "difficulty": 3, "personalization_score": 8},
    {"code": "documentary_life", "title": "Документальный фильм", "kind": "video", "category": "emotional", "occasion_codes": ["birthday", "anniversary", "wedding"], "relationship_types": ["parent", "spouse", "sibling"], "moods": ["touching", "nostalgic"], "base_price_rub": 799, "estimated_duration_sec": 70, "difficulty": 3, "personalization_score": 9},
    {"code": "rap_battle", "title": "Рэп-поздравление", "kind": "video", "category": "music", "occasion_codes": ["birthday"], "relationship_types": ["friend", "colleague", "classmate"], "moods": ["funny", "epic"], "base_price_rub": 899, "estimated_duration_sec": 60, "difficulty": 4, "personalization_score": 8},
    {"code": "oscar_award", "title": "Оскар", "kind": "video", "category": "cinematic", "occasion_codes": ["birthday", "anniversary", "achievement"], "relationship_types": RELATIONSHIP_TYPES, "moods": ["epic", "official"], "base_price_rub": 799, "estimated_duration_sec": 55, "difficulty": 3, "personalization_score": 8},
    {"code": "president_address", "title": "Президентское обращение", "kind": "video", "category": "humor", "occasion_codes": ["birthday", "anniversary"], "relationship_types": ["boss", "colleague", "parent"], "moods": ["official", "funny"], "base_price_rub": 699, "estimated_duration_sec": 45, "difficulty": 2, "personalization_score": 7},
    {"code": "space_mission", "title": "Космическая миссия", "kind": "video", "category": "cinematic", "occasion_codes": ["birthday", "new_year"], "relationship_types": ["friend", "partner", "spouse"], "moods": ["epic", "warm"], "base_price_rub": 799, "estimated_duration_sec": 60, "difficulty": 3, "personalization_score": 9},
    {"code": "alien_greeting", "title": "Инопланетяне", "kind": "video", "category": "humor", "occasion_codes": ["birthday"], "relationship_types": ["friend", "classmate", "sibling"], "moods": ["funny", "surprising"], "base_price_rub": 599, "estimated_duration_sec": 45, "difficulty": 2, "personalization_score": 7},
    {"code": "matrix_style", "title": "Матрица", "kind": "video", "category": "cinematic", "occasion_codes": ["birthday"], "relationship_types": ["friend", "colleague", "classmate"], "moods": ["epic", "brutal"], "base_price_rub": 699, "estimated_duration_sec": 50, "difficulty": 3, "personalization_score": 8},
    {"code": "love_letter", "title": "Любовное письмо", "kind": "video", "category": "romantic", "occasion_codes": ["anniversary", "wedding", "valentines"], "relationship_types": ["spouse", "partner"], "moods": ["romantic", "touching"], "base_price_rub": 699, "estimated_duration_sec": 55, "difficulty": 2, "personalization_score": 9},
    {"code": "cinematic_love", "title": "Кино о любви", "kind": "video", "category": "romantic", "occasion_codes": ["anniversary", "wedding"], "relationship_types": ["spouse", "partner"], "moods": ["romantic", "warm"], "base_price_rub": 799, "estimated_duration_sec": 60, "difficulty": 3, "personalization_score": 9},
    {"code": "romantic_trailer", "title": "Романтический трейлер", "kind": "video", "category": "romantic", "occasion_codes": ["anniversary", "wedding", "valentines"], "relationship_types": ["spouse", "partner"], "moods": ["romantic", "epic"], "base_price_rub": 799, "estimated_duration_sec": 55, "difficulty": 3, "personalization_score": 8},
    {"code": "couple_journey", "title": "Путешествие пары", "kind": "video", "category": "romantic", "occasion_codes": ["anniversary", "wedding"], "relationship_types": ["spouse", "partner"], "moods": ["romantic", "nostalgic"], "base_price_rub": 699, "estimated_duration_sec": 50, "difficulty": 2, "personalization_score": 8},
    {"code": "how_we_met", "title": "История знакомства", "kind": "video", "category": "romantic", "occasion_codes": ["anniversary", "wedding"], "relationship_types": ["spouse", "partner"], "moods": ["touching", "nostalgic"], "base_price_rub": 699, "estimated_duration_sec": 55, "difficulty": 2, "personalization_score": 9},
    {"code": "from_kids_to_parents", "title": "От детей родителям", "kind": "video", "category": "family", "occasion_codes": ["birthday", "anniversary"], "relationship_types": ["child", "parent"], "moods": ["touching", "warm"], "base_price_rub": 599, "estimated_duration_sec": 50, "difficulty": 2, "personalization_score": 8},
    {"code": "from_parents_to_child", "title": "От родителей ребёнку", "kind": "video", "category": "family", "occasion_codes": ["birthday", "new_year"], "relationship_types": ["parent", "child"], "moods": ["warm", "festive"], "base_price_rub": 599, "estimated_duration_sec": 45, "difficulty": 1, "personalization_score": 7},
    {"code": "family_chronicles", "title": "Семейная хроника", "kind": "video", "category": "family", "occasion_codes": ["birthday", "anniversary"], "relationship_types": ["parent", "child", "sibling", "grandparent"], "moods": ["nostalgic", "warm"], "base_price_rub": 799, "estimated_duration_sec": 70, "difficulty": 3, "personalization_score": 8},
    {"code": "family_movie", "title": "Семейный фильм", "kind": "video", "category": "family", "occasion_codes": ["birthday", "new_year"], "relationship_types": RELATIONSHIP_TYPES, "moods": ["warm", "funny"], "base_price_rub": 699, "estimated_duration_sec": 55, "difficulty": 2, "personalization_score": 7},
    {"code": "thanks_for_everything", "title": "Спасибо за всё", "kind": "video", "category": "emotional", "occasion_codes": ["birthday", "anniversary"], "relationship_types": ["parent", "spouse", "teacher"], "moods": ["touching", "warm"], "base_price_rub": 699, "estimated_duration_sec": 55, "difficulty": 2, "personalization_score": 9},
    {"code": "colleagues_funny", "title": "От коллег", "kind": "video", "category": "corporate", "occasion_codes": ["birthday", "professional_holiday"], "relationship_types": ["colleague", "boss", "employee"], "moods": ["funny", "official"], "base_price_rub": 599, "estimated_duration_sec": 45, "difficulty": 2, "personalization_score": 7},
    {"code": "from_boss_to_employee", "title": "От руководителя", "kind": "video", "category": "corporate", "occasion_codes": ["birthday", "professional_holiday"], "relationship_types": ["boss", "employee"], "moods": ["official", "warm"], "base_price_rub": 699, "estimated_duration_sec": 50, "difficulty": 2, "personalization_score": 7},
    {"code": "employee_award", "title": "Награда сотруднику", "kind": "video", "category": "corporate", "occasion_codes": ["achievement", "professional_holiday"], "relationship_types": ["boss", "employee"], "moods": ["official", "epic"], "base_price_rub": 799, "estimated_duration_sec": 55, "difficulty": 3, "personalization_score": 8},
    {"code": "corporate_news", "title": "Корпоративные новости", "kind": "video", "category": "corporate", "occasion_codes": ["new_year", "professional_holiday"], "relationship_types": ["colleague", "boss"], "moods": ["official", "funny"], "base_price_rub": 599, "estimated_duration_sec": 45, "difficulty": 2, "personalization_score": 6},
    {"code": "ceo_greeting", "title": "CEO обращается к сотруднику", "kind": "video", "category": "corporate", "occasion_codes": ["birthday", "anniversary"], "relationship_types": ["boss", "employee"], "moods": ["official", "warm"], "base_price_rub": 699, "estimated_duration_sec": 50, "difficulty": 2, "personalization_score": 7},
    {"code": "march8_women", "title": "8 марта — женщине", "kind": "video", "category": "holiday", "occasion_codes": ["march8"], "relationship_types": ["spouse", "parent", "colleague", "friend"], "moods": ["warm", "romantic"], "base_price_rub": 599, "estimated_duration_sec": 45, "difficulty": 1, "personalization_score": 7},
    {"code": "feb23_men", "title": "23 февраля — мужчине", "kind": "video", "category": "holiday", "occasion_codes": ["feb23"], "relationship_types": ["spouse", "parent", "colleague", "friend"], "moods": ["brutal", "official"], "base_price_rub": 599, "estimated_duration_sec": 45, "difficulty": 2, "personalization_score": 7},
    {"code": "new_year_wishes", "title": "Новый год — поздравление", "kind": "video", "category": "holiday", "occasion_codes": ["new_year"], "relationship_types": RELATIONSHIP_TYPES, "moods": ["festive", "warm", "funny"], "base_price_rub": 599, "estimated_duration_sec": 50, "difficulty": 1, "personalization_score": 6},
    {"code": "wedding_congrats", "title": "С днём свадьбы", "kind": "video", "category": "wedding", "occasion_codes": ["wedding", "anniversary"], "relationship_types": ["friend", "spouse", "parent", "sibling"], "moods": ["romantic", "warm"], "base_price_rub": 699, "estimated_duration_sec": 55, "difficulty": 2, "personalization_score": 8},
    {"code": "anniversary_epic", "title": "Юбилей — эпично", "kind": "video", "category": "birthday", "occasion_codes": ["birthday", "anniversary"], "relationship_types": RELATIONSHIP_TYPES, "moods": ["epic", "warm"], "base_price_rub": 799, "estimated_duration_sec": 60, "difficulty": 3, "personalization_score": 8},
    {"code": "kids_song", "title": "Детская песня-поздравление", "kind": "video", "category": "family", "occasion_codes": ["birthday", "new_year"], "relationship_types": ["child", "parent", "grandparent"], "moods": ["festive", "funny"], "base_price_rub": 499, "estimated_duration_sec": 40, "difficulty": 1, "personalization_score": 6},
    {"code": "grandparents_touching", "title": "Бабушке/дедушке", "kind": "video", "category": "family", "occasion_codes": ["birthday", "anniversary"], "relationship_types": ["grandparent"], "moods": ["touching", "warm"], "base_price_rub": 599, "estimated_duration_sec": 50, "difficulty": 1, "personalization_score": 8},
    {"code": "sport_commentator", "title": "Спортивный комментатор", "kind": "video", "category": "humor", "occasion_codes": ["birthday"], "relationship_types": ["friend", "colleague", "classmate"], "moods": ["funny", "epic"], "base_price_rub": 599, "estimated_duration_sec": 50, "difficulty": 2, "personalization_score": 7},
    {"code": "police_protocol", "title": "Полицейский протокол", "kind": "video", "category": "humor", "occasion_codes": ["birthday"], "relationship_types": ["friend", "colleague", "classmate"], "moods": ["funny", "brutal"], "base_price_rub": 599, "estimated_duration_sec": 50, "difficulty": 2, "personalization_score": 7},
    {"code": "military_communique", "title": "Военная сводка", "kind": "video", "category": "humor", "occasion_codes": ["feb23", "victory_day", "birthday"], "relationship_types": ["friend", "colleague", "classmate"], "moods": ["official", "funny"], "base_price_rub": 599, "estimated_duration_sec": 50, "difficulty": 2, "personalization_score": 7},
    {"code": "medal_ceremony", "title": "Церемония награждения", "kind": "video", "category": "cinematic", "occasion_codes": ["birthday", "achievement", "anniversary"], "relationship_types": RELATIONSHIP_TYPES, "moods": ["epic", "official"], "base_price_rub": 799, "estimated_duration_sec": 55, "difficulty": 3, "personalization_score": 8},
    {"code": "retro_ussr", "title": "СССР-ретро", "kind": "video", "category": "thematic", "occasion_codes": ["birthday", "victory_day", "feb23", "march8"], "relationship_types": ["parent", "grandparent", "classmate"], "moods": ["nostalgic", "funny"], "base_price_rub": 699, "estimated_duration_sec": 55, "difficulty": 2, "personalization_score": 8},
]


async def seed():
    async with async_session_factory() as db:
        # Seed relationship types
        for code in RELATIONSHIP_TYPES:
            existing = await db.execute(
                __import__("sqlalchemy").select(RelationshipType).where(RelationshipType.code == code)
            )
            if existing.scalar_one_or_none():
                continue
            db.add(RelationshipType(code=code, title=code.title(), sort_order=RELATIONSHIP_TYPES.index(code), is_active=True))

        # Seed holidays
        for holiday in HOLIDAYS:
            existing = await db.execute(
                __import__("sqlalchemy").select(Holiday).where(Holiday.code == holiday["code"])
            )
            if existing.scalar_one_or_none():
                continue
            db.add(Holiday(**holiday, status="active", metadata_={}))

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
                qa_checklist={
                    "script_checked": True,
                    "face_ok": True,
                    "voice_ok": True,
                    "text_ok": True,
                    "duration_ok": True,
                    "cost_known": True,
                },
                variant_group="birthday_warm_v1",
                variant_name="control",
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
                condition={
                    "field": "recipient.age",
                    "operator": ">=",
                    "value": 18,
                    "then": "main_scene",
                    "else": "main_scene_soft",
                },
            )
            db.add(scene)
            print(f"Created template: {tpl_data['code']}")

        await db.commit()
        print("Seed completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
