from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.gallery import GalleryStatus


class GallerySubmissionCreate(BaseModel):
    generation_id: UUID
    title: str
    description: str | None = None
    consent_given: bool = False


class GallerySubmissionResponse(BaseModel):
    id: UUID
    generation_id: UUID
    user_id: UUID
    project_id: UUID
    title: str
    description: str | None = None
    thumbnail_url: str | None = None
    video_url: str | None = None
    status: GalleryStatus
    is_public: bool
    consent_given: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GalleryListResponse(BaseModel):
    items: list[GallerySubmissionResponse]
