from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TemplateResponse(BaseModel):
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
    estimated_duration_sec: int | None = None
    personalization_score: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TemplateListResponse(BaseModel):
    items: list[TemplateResponse]
    total: int
    page: int
    page_size: int


class RecommendationResponse(BaseModel):
    id: UUID
    project_id: UUID
    template_version_id: UUID
    status: str
    rank: int
    score: float | None = None
    match_reasons: list[str] = []
    explanation: str | None = None
    generated_by_model: str | None = None
    created_at: datetime
    selected_at: datetime | None = None

    model_config = {"from_attributes": True}


class RecommendationListResponse(BaseModel):
    items: list[RecommendationResponse]


class RecommendationSelectResponse(BaseModel):
    id: UUID
    project_id: UUID
    selected_template_version_id: UUID
    status: str

    model_config = {"from_attributes": True}
