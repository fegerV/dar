from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AssetUploadRequest(BaseModel):
    type: str = Field(..., pattern="^(photo|image|video|audio|voice|music|thumbnail|subtitle|script|document|source)$")
    filename: str = Field(..., min_length=1, max_length=255)
    mime_type: str | None = None
    size_bytes: int | None = Field(None, ge=0)


class AssetUploadResponse(BaseModel):
    asset_id: UUID
    upload_url: str
    expires_in: int = 900


class AssetResponse(BaseModel):
    id: UUID
    type: str
    status: str
    title: str | None = None
    description: str | None = None
    mime_type: str | None = None
    duration_sec: float | None = None
    width: int | None = None
    height: int | None = None
    url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AssetListResponse(BaseModel):
    items: list[AssetResponse]
    total: int
    page: int
    page_size: int
