from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BriefUpdate(BaseModel):
    occasion_text: str | None = None
    sender_role: str | None = None
    recipient_role: str | None = None
    relationship: str | None = None
    relationship_text: str | None = None
    desired_mood: str | None = None
    desired_length_sec: int | None = Field(None, ge=3, le=300)
    humor_level: int | None = Field(None, ge=0, le=100)
    emotion_level: int | None = Field(None, ge=0, le=100)
    surprise_level: int | None = Field(None, ge=0, le=100)
    personalization_level: int | None = Field(None, ge=0, le=100)
    inside_joke: str | None = None
    hobbies_text: str | None = None
    character_traits: str | None = None
    memorable_story: str | None = None
    desired_phrase: str | None = None
    forbidden_topics: str | None = None
    sender_message: str | None = None
    personalization_answers: dict | None = None
    selected_options: dict | None = None


class BriefResponse(BaseModel):
    id: UUID
    project_id: UUID
    status: str
    occasion_text: str | None = None
    sender_role: str | None = None
    recipient_role: str | None = None
    relationship: str | None = None
    relationship_text: str | None = None
    desired_mood: str | None = None
    desired_length_sec: int | None = None
    humor_level: int | None = None
    emotion_level: int | None = None
    surprise_level: int | None = None
    personalization_level: int | None = None
    inside_joke: str | None = None
    hobbies_text: str | None = None
    character_traits: str | None = None
    memorable_story: str | None = None
    desired_phrase: str | None = None
    forbidden_topics: str | None = None
    sender_message: str | None = None
    personalization_answers: dict = {}
    selected_options: dict = {}
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class BriefCompleteResponse(BaseModel):
    project_id: UUID
    status: str
