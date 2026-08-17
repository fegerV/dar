from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    recipient_id: UUID
    occasion_code: str = Field(min_length=1, max_length=50)
    occasion_title: str | None = None
    title: str | None = None


class ProjectUpdate(BaseModel):
    title: str | None = None
    requested_delivery_at: datetime | None = None


class ProjectResponse(BaseModel):
    id: UUID
    owner_user_id: UUID
    recipient_id: UUID | None = None
    title: str | None = None
    status: str
    visibility: str
    occasion_code: str | None = None
    occasion_title: str | None = None
    selected_recommendation_id: UUID | None = None
    selected_template_version_id: UUID | None = None
    final_generation_id: UUID | None = None
    price_rub: float
    bonus_discount_rub: float
    promo_discount_rub: float
    paid_rub: float
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int
