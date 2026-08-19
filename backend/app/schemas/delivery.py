from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DeliveryCreate(BaseModel):
    channel: str = Field(..., pattern="^(telegram|vk|whatsapp|link|download|email|other)$")
    destination: str | None = None
    expires_in_days: int = Field(30, ge=1, le=365)
    max_views: int | None = Field(None, ge=1)
    password: str | None = Field(None, min_length=1)
    scheduled_at: datetime | None = None
    timezone: str | None = None


class DeliveryResponse(BaseModel):
    id: UUID
    project_id: UUID
    channel: str
    status: str
    destination: str | None = None
    public_url: str | None = None
    created_at: datetime
    scheduled_at: datetime | None = None
    gift_fulfillment_status: str | None = None
    sent_at: datetime | None = None
    opened_at: datetime | None = None

    model_config = {"from_attributes": True}


class DeliveryListResponse(BaseModel):
    items: list[DeliveryResponse]


class ShareLinkResponse(BaseModel):
    token: str
    public_url: str
    expires_at: datetime | None = None
    max_views: int | None = None
    password_protected: bool = False


class PublicShareView(BaseModel):
    project_id: UUID
    title: str | None = None
    status: str
    recipient_name: str | None = None
    video_url: str | None = None
    thumbnail_url: str | None = None
    duration_sec: int | None = None
    referral_code: str | None = None

    model_config = {"from_attributes": True}


class PublicShareAccessRequest(BaseModel):
    password: str | None = None
