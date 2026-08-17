from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HolidayResponse(BaseModel):
    id: UUID
    code: str
    title: str
    kind: str
    month: int | None = None
    day: int | None = None
    country_code: str | None = None
    description: str | None = None
    status: str
    metadata: dict = {}
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
