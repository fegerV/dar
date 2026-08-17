from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


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
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class GenerationListResponse(BaseModel):
    items: list[GenerationResponse]
    total: int
    page: int
    page_size: int
