from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

VALID_REACTIONS = {"fire", "heart", "laugh", "cry", "neutral"}


class ReactionEnum(str, Enum):
    fire = "fire"
    heart = "heart"
    laugh = "laugh"
    cry = "cry"
    neutral = "neutral"


class ReactionRequest(BaseModel):
    emoji: ReactionEnum
    rating: int | None = Field(None, ge=1, le=5)
    comment: str | None = Field(None, max_length=2000)
    negative_details: dict | None = None


class ReactionResponse(BaseModel):
    id: UUID
    project_id: UUID
    emoji: str
    rating: int | None = None
    comment: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReactionStatsResponse(BaseModel):
    project_id: UUID
    total_reactions: int = 0
    by_emoji: dict[str, int] = Field(default_factory=dict)
    average_rating: float | None = None
    negative_count: int = 0
