from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class HolidayInfo(BaseModel):
    code: str
    title: str
    kind: str
    country_code: str | None = None
    description: str | None = None
    source: str | None = None


class TodayPackResponse(BaseModel):
    date: str
    holidays: list[HolidayInfo] = Field(default_factory=list)
    upcoming_events: list[dict[str, Any]] = Field(default_factory=list)
    active_projects_count: int = 0
    active_projects: list[UUID] = Field(default_factory=list)
