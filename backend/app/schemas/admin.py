from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AdminTemplateCreate(BaseModel):
    code: str
    title: str
    description: str | None = None
    kind: str = "video"
    category: str | None = None
    occasion_codes: list[str] = []
    relationship_types: list[str] = []
    moods: list[str] = []
    base_price_rub: float = 0


class AdminTemplateResponse(BaseModel):
    id: UUID
    code: str
    title: str
    description: str | None = None
    kind: str
    status: str
    category: str | None = None
    occasion_codes: list[str] = []
    relationship_types: list[str] = []
    moods: list[str] = []
    base_price_rub: float
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminUserResponse(BaseModel):
    id: UUID
    status: str
    email: str | None = None
    display_name: str | None = None
    is_admin: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminDashboardStats(BaseModel):
    total_users: int
    total_projects: int
    total_payments: float
    pending_reviews: int
    active_generations: int
