from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator


class GenerationStartRequest(BaseModel):
    force_regenerate: bool = False
    variables: dict | None = None


class GenerationStepResponse(BaseModel):
    id: UUID
    step_no: int
    step_code: str
    type: str
    status: str
    input_json: dict = {}
    output_json: dict = {}
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class GenerationResponse(BaseModel):
    id: UUID
    project_id: UUID
    type: str
    status: str
    progress: int
    current_step: str | None = None
    estimated_seconds: int | None = None
    error_code: str | None = None
    error_message: str | None = None
    output_assets: list[dict] = []
    video_url: str | None = None
    thumbnail_url: str | None = None
    preview_url: str | None = None
    preview_thumbnail_url: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _extract_urls(cls, data):
        output_json = getattr(data, "output_json", None) or {}
        if isinstance(output_json, dict):
            data_dict = dict(data.__dict__) if hasattr(data, "__dict__") else data
            data_dict["video_url"] = output_json.get("video_url")
            data_dict["thumbnail_url"] = output_json.get("thumbnail_url")
            data_dict["preview_url"] = output_json.get("preview_url")
            data_dict["preview_thumbnail_url"] = output_json.get("preview_thumbnail_url")
            return data_dict
        return data


class GenerationListResponse(BaseModel):
    items: list[GenerationResponse]
    total: int
    page: int
    page_size: int
