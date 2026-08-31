from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ImagePreflightRequest(BaseModel):
    generation_id: UUID
    image_url: str
    image_metadata: dict | None = None


class ImagePreflightResponse(BaseModel):
    id: UUID
    generation_id: UUID | None = None
    image_url: str
    quality_score: float | None = None
    face_count: int | None = None
    face_size: str | None = None
    pose: str | None = None
    sharpness: float | None = None
    recommended_models: list[str] = []
    recommended_templates: list[str] = []
    issues: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoRecipeResponse(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None = None
    template_code: str
    model_name: str
    model_version: str | None = None
    prompt: str | None = None
    negative_strategy: str | None = None
    duration_sec: int | None = None
    camera: str | None = None
    motion: str | None = None
    speech: bool | None = None
    cost_estimate: float | None = None
    success_rate: float | None = None
    avg_generations: float | None = None
    last_tested_at: datetime | None = None
    is_active: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class RecipeFailureResponse(BaseModel):
    id: UUID
    recipe_id: UUID
    condition: str
    severity: str | None = None
    recommendation: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerationFailureResponse(BaseModel):
    id: UUID
    generation_id: UUID
    failure_codes: list[str] = []
    repaired_prompt: str | None = None
    repaired_negative: str | None = None
    repaired_model: str | None = None
    repaired_template: str | None = None
    attempt: int | None = None
    critic_overall: float | None = None
    critic_decision: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserFeedbackRequest(BaseModel):
    generation_id: UUID
    rating: str | None = None
    reason: str | None = None
    comment: str | None = None


class UserFeedbackResponse(BaseModel):
    id: UUID
    generation_id: UUID
    rating: str | None = None
    reason: str | None = None
    comment: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ModelProfileResponse(BaseModel):
    id: UUID
    model_name: str
    provider: str | None = None
    version: str | None = None
    cost_per_sec: float | None = None
    avg_generation_time_sec: float | None = None
    supports_image_to_video: bool | None = None
    supports_audio: bool | None = None
    supports_control: bool | None = None
    preferred_scenes: list[str] = []
    known_weaknesses: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}
