from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class RecipientCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=200)
    last_name: str | None = None
    nickname: str | None = None
    gender: str | None = Field(None, pattern="^(male|female|other)$")
    birth_date: date | None = None
    city: str | None = None
    occupation: str | None = None
    relationship: str | None = None
    relationship_label: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    notes: str | None = None
    interests: list[str] = Field(default_factory=list)
    traits: list[str] = Field(default_factory=list)
    favorite_things: list[str] = Field(default_factory=list)
    forbidden_topics: list[str] = Field(default_factory=list)


class RecipientUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=200)
    last_name: str | None = None
    nickname: str | None = None
    gender: str | None = Field(None, pattern="^(male|female|other)$")
    birth_date: date | None = None
    city: str | None = None
    occupation: str | None = None
    relationship: str | None = None
    relationship_label: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    notes: str | None = None
    interests: list[str] | None = None
    traits: list[str] | None = None
    favorite_things: list[str] | None = None
    forbidden_topics: list[str] | None = None


class RecipientResponse(BaseModel):
    id: UUID
    status: str
    first_name: str
    last_name: str | None = None
    nickname: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    city: str | None = None
    occupation: str | None = None
    relationship: str | None = None
    relationship_label: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    notes: str | None = None
    interests: list[str] = []
    traits: list[str] = []
    favorite_things: list[str] = []
    forbidden_topics: list[str] = []
    photo_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _compute_photo_url(cls, data):
        recipient_assets = getattr(data, "recipient_assets", None)
        if recipient_assets is not None:
            primary = next(
                (ra for ra in recipient_assets if ra.is_primary),
                None,
            )
            if primary and primary.asset:
                data_dict = dict(data.__dict__)
                data_dict["photo_url"] = f"assets/{primary.asset.id}"
                return data_dict
        return data


class RecipientListResponse(BaseModel):
    items: list[RecipientResponse]
    total: int
    page: int
    page_size: int


class RecipientPhotoUploadRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    mime_type: str | None = None
    size_bytes: int | None = Field(None, ge=0)


class RecipientPhotoUploadResponse(BaseModel):
    asset_id: UUID
    upload_url: str
    expires_in: int = 900
