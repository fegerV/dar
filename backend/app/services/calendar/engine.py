from datetime import date, datetime, timedelta, timezone
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.holiday import Holiday
from app.models.project import Project

RECIPIENT_AGE_KEY = "recipient_age"
RELATIONSHIP_KEY = "relationship"
OCCASION_KEY = "occasion"

VALID_COMPARISONS = {"eq", "ne", "lt", "lte", "gt", "gte"}
VALID_LOGIC = {"and", "or"}


class CalendarEngine:
    HOLIDAYS_2024_2026 = {
        date(2024, 1, 1): ("new_year", "Новый год", "national"),
        date(2024, 1, 7): ("orthodox_christmas", "Рождество", "religious"),
        date(2024, 2, 14): ("valentines_day", "День валентина", "love"),
        date(2024, 2, 19): ("black_history_month_end", "Конец месяцы истории", "observance"),
        date(2024, 3, 8): ("womens_day", "Международный женский день", "professional"),
        date(2024, 3, 17): ("irish_day", "День Ирландии", "cultural"),
        date(2024, 4, 1): ("april_fools", "День дурака", "cultural"),
        date(2024, 4, 7): ("orthodox_easter", "Великую Пасху", "religious"),
        date(2024, 5, 1): ("labour_day", "Праздник труда", "professional"),
        date(2024, 5, 9): ("victory_day", "День Победы", "national"),
        date(2024, 6, 16): ("fathers_day_us", "День отца (США)", "observance"),
        date(2024, 6, 23): ("winter_day", "День зимы", "national"),
        date(2024, 7, 7): ("day_of_russia", "День России", "national"),
        date(2024, 7, 12): ("fathers_day_ru", "День отца (РФ)", "observance"),
        date(2024, 8, 2): ("mothers_day_ru", "День матери", "observance"),
        date(2024, 8, 8): ("mothers_day_us", "День матери (США)", "observance"),
        date(2024, 9, 1): ("knowledge_day", "День знаний", "national"),
        date(2024, 9, 2): ("grandmothers_day", "День бабушки", "observance"),
        date(2024, 9, 23): ("autumn_equinox", "Осеннее равноденствие", "observance"),
        date(2024, 10, 13): ("fathers_day_au", "День отца (Австралия)", "observance"),
        date(2024, 10, 28): ("new_years_eve_approach", "Подготовка к Новому году", "cultural"),
        date(2024, 11, 1): ("halloween", "Хэллоуин", "cultural"),
        date(2024, 11, 28): ("thanksgiving_us", "День благодарения (США)", "cultural"),
        date(2024, 11, 29): ("black_friday", "Чёрная пятница", "commercial"),
        date(2024, 12, 25): ("christmas", "Рождество", "religious"),
        date(2025, 1, 1): ("new_year", "Новый год", "national"),
        date(2025, 1, 7): ("orthodox_christmas", "Рождество", "religious"),
        date(2025, 2, 14): ("valentines_day", "День валентина", "love"),
        date(2025, 3, 8): ("womens_day", "Международный женский день", "professional"),
        date(2025, 3, 17): ("irish_day", "День Ирландии", "cultural"),
        date(2025, 4, 1): ("april_fools", "День дурака", "cultural"),
        date(2025, 4, 20): ("orthodox_easter", "Великую Пасху", "religious"),
        date(2025, 5, 1): ("labour_day", "Праздник труда", "professional"),
        date(2025, 5, 9): ("victory_day", "День Победы", "national"),
        date(2025, 6, 15): ("fathers_day_us", "День отца (США)", "observance"),
        date(2025, 6, 23): ("winter_day", "День зимы", "national"),
        date(2025, 7, 7): ("day_of_russia", "День России", "national"),
        date(2025, 7, 13): ("fathers_day_ru", "День отца (РФ)", "observance"),
        date(2025, 8, 2): ("mothers_day_ru", "День матери", "observance"),
        date(2025, 8, 10): ("mothers_day_us", "День матери (США)", "observance"),
        date(2025, 9, 1): ("knowledge_day", "День знаний", "national"),
        date(2025, 9, 7): ("autumn_equinox", "Осеннее равноденствие", "observance"),
        date(2025, 10, 26): ("new_years_eve_approach", "Подготовка к Новому году", "cultural"),
        date(2025, 11, 1): ("halloween", "Хэллоуин", "cultural"),
        date(2025, 11, 27): ("thanksgiving_us", "День благодарения (США)", "cultural"),
        date(2025, 11, 28): ("black_friday", "Чёрная пятница", "commercial"),
        date(2025, 12, 25): ("christmas", "Рождество", "religious"),
        date(2026, 1, 1): ("new_year", "Новый год", "national"),
        date(2026, 1, 7): ("orthodox_christmas", "Рождество", "religious"),
        date(2026, 2, 14): ("valentines_day", "День валентина", "love"),
        date(2026, 3, 8): ("womens_day", "Международный женский день", "professional"),
        date(2026, 3, 17): ("irish_day", "День Ирландии", "cultural"),
        date(2026, 4, 1): ("april_fools", "День дурака", "cultural"),
        date(2026, 4, 12): ("orthodox_easter", "Великую Пасху", "religious"),
        date(2026, 5, 1): ("labour_day", "Праздник труда", "professional"),
        date(2026, 5, 9): ("victory_day", "День Победы", "national"),
        date(2026, 6, 21): ("fathers_day_us", "День отца (США)", "observance"),
        date(2026, 6, 23): ("winter_day", "День зимы", "national"),
        date(2026, 7, 7): ("day_of_russia", "День России", "national"),
        date(2026, 7, 12): ("fathers_day_ru", "День отца (РФ)", "observance"),
        date(2026, 8, 2): ("mothers_day_ru", "День матери", "observance"),
        date(2026, 8, 9): ("mothers_day_us", "День матери (США)", "observance"),
        date(2026, 9, 1): ("knowledge_day", "День знаний", "national"),
        date(2026, 9, 22): ("autumn_equinox", "Осеннее равноденствие", "observance"),
        date(2026, 10, 25): ("new_years_eve_approach", "Подготовка к Новому году", "cultural"),
        date(2026, 11, 1): ("halloween", "Хэллоуин", "cultural"),
        date(2026, 11, 26): ("thanksgiving_us", "День благодарения (США)", "cultural"),
        date(2026, 11, 27): ("black_friday", "Чёрная пятница", "commercial"),
        date(2026, 12, 25): ("christmas", "Рождество", "religious"),
    }

    PROFESSIONAL_DAYS = {
        date(2024, 1, 24): ("researcher_day", "День учёного"),
        date(2024, 2, 23): ("defender_day", "День защитника Отечества"),
        date(2024, 3, 13): ("astrophysicist_day", "День астрофизика"),
        date(2024, 4, 12): ("cosmonaut_day", "День космонавтики"),
        date(2024, 5, 13): ("tea_day", "День чая"),
        date(2024, 6, 12): ("russia_day", "День России"),
        date(2024, 7, 28): ("doctors_day", "День врача"),
        date(2024, 8, 11): ("builder_day", "День строителя"),
        date(2024, 9, 1): ("knowledge_day", "День знаний"),
        date(2024, 10, 1): ("teacher_day", "День учителя"),
        date(2024, 11, 7): ("October_revolution", "Октябрьская революция"),
        date(2024, 11, 20): ("sorters_day", "День ракушек"),
        date(2024, 12, 3): ("_disabled_person_day", "День инвалида"),
        date(2024, 12, 12): ("constitution_day", "День Конституции"),
        date(2025, 1, 24): ("researcher_day", "День учёного"),
        date(2025, 2, 23): ("defender_day", "День защитника Отечества"),
        date(2025, 3, 13): ("astrophysicist_day", "День астрофизика"),
        date(2025, 4, 12): ("cosmonaut_day", "День космонавтики"),
        date(2025, 5, 13): ("tea_day", "День чая"),
        date(2025, 6, 12): ("russia_day", "День России"),
        date(2025, 7, 28): ("doctors_day", "День врача"),
        date(2025, 8, 11): ("builder_day", "День строителя"),
        date(2025, 9, 1): ("knowledge_day", "День знаний"),
        date(2025, 10, 1): ("teacher_day", "День учителя"),
        date(2025, 11, 7): ("October_revolution", "Октябрьская революция"),
        date(2025, 11, 20): ("sorters_day", "День ракушек"),
        date(2025, 12, 3): ("disabled_person_day", "День инвалида"),
        date(2025, 12, 12): ("constitution_day", "День Конституции"),
    }

    MONTH_DAY_HOLIDAYS = {
        (1, 2): ("day_after_new_year", "День после Нового года"),
        (2, 23): ("defender_day", "День защитника Отечества"),
        (3, 8): ("womens_day", "Женский день"),
        (5, 1): ("labour_day", "Праздник труда"),
        (5, 9): ("victory_day", "День Победы"),
        (6, 12): ("russia_day", "День России"),
        (7, 28): ("doctors_day", "День врача"),
        (8, 8): ("mothers_day", "День матери"),
        (9, 1): ("knowledge_day", "День знаний"),
        (9, 7): ("teacher_day", "День учителя"),
        (11, 7): ("october_revolution_day", "Октябрьская революция"),
        (12, 12): ("constitution_day", "День Конституции"),
        (10, 31): ("halloween", "Хэллоуин"),
        (12, 25): ("christmas", "Рождество"),
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_todays_holidays(self, today: date | None = None) -> list[dict]:
        today = today or datetime.now(timezone.utc).date()
        results = []

        holiday_result = await self.db.execute(
            select(Holiday).where(
                sa.or_(
                    sa.and_(Holiday.month == today.month, Holiday.day == today.day),
                    sa.and_(
                        sa.func.extract("month", Holiday.month) == today.month,
                        sa.func.extract("day", Holiday.day) == today.day,
                    ),
                )
            )
        )
        db_holidays = holiday_result.scalars().all()
        for h in db_holidays:
            results.append({
                "code": h.code,
                "title": h.title,
                "kind": h.kind,
                "country_code": h.country_code,
                "description": h.description,
                "source": "db",
            })

        if today in self.HOLIDAYS_2024_2026:
            code, title, kind = self.HOLIDAYS_2024_2026[today]
            if not any(r["code"] == code for r in results):
                results.append({
                    "code": code,
                    "title": title,
                    "kind": kind,
                    "country_code": "RU",
                    "description": title,
                    "source": "builtin",
                })

        if today in self.PROFESSIONAL_DAYS:
            code, title = self.PROFESSIONAL_DAYS[today]
            if not any(r["code"] == code for r in results):
                results.append({
                    "code": code,
                    "title": title,
                    "kind": "professional",
                    "country_code": "RU",
                    "description": title,
                    "source": "builtin",
                })

        key = (today.month, today.day)
        if key in self.MONTH_DAY_HOLIDAYS:
            code, title = self.MONTH_DAY_HOLIDAYS[key]
            if not any(r["code"] == code for r in results):
                results.append({
                    "code": code,
                    "title": title,
                    "kind": "national",
                    "country_code": "RU",
                    "description": title,
                    "source": "builtin",
                })

        return results

    async def get_today_pack(self, user_id: UUID) -> dict:
        today = datetime.now(timezone.utc).date()
        holidays = await self.get_todays_holidays(today)

        upcoming_events = []
        for delta in range(1, 8):
            future_date = today + timedelta(days=delta)
            future_holidays = await self.get_todays_holidays(future_date)
            for h in future_holidays:
                upcoming_events.append({
                    "date": future_date.isoformat(),
                    **h,
                })

        active_projects_result = await self.db.execute(
            select(Project).where(
                Project.owner_user_id == user_id,
                Project.status.in_(["draft", "brief_completed"]),
                Project.requested_delivery_at >= datetime.now(timezone.utc),
            )
        )
        active_projects = active_projects_result.scalars().all()

        return {
            "date": today.isoformat(),
            "holidays": holidays,
            "upcoming_events": upcoming_events[:10],
            "active_projects_count": len(active_projects),
            "active_projects": [p.id for p in active_projects],
        }

    async def get_holiday_by_code(self, code: str) -> Holiday | None:
        result = await self.db.execute(select(Holiday).where(Holiday.code == code))
        return result.scalar_one_or_none()

    async def find_holiday_near(self, target_date: date, days_ahead: int = 30) -> list[dict]:
        results = []
        for delta in range(0, days_ahead + 1):
            check_date = target_date + timedelta(days=delta)
            holidays = await self.get_todays_holidays(check_date)
            for h in holidays:
                results.append({"date": check_date.isoformat(), **h})
        return results
