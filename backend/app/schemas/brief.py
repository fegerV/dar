from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CreativeBriefRead(BaseModel):
    recipient: dict[str, Any] | None = None
    relationship_: str | None = None
    personality: list[str] | None = None
    interests: list[str] | None = None
    inside_joke: str | None = None
    sender_message: str | None = None
    occasion_text: str | None = None
    sender_role: str | None = None
    recipient_role: str | None = None
    relationship_text: str | None = None
    desired_mood: str | None = None
    desired_length_sec: int | None = None
    humor_level: int | None = None
    emotion_level: int | None = None
    surprise_level: int | None = None
    personalization_level: int | None = None
    character_traits: str | None = None
    memorable_story: str | None = None
    desired_phrase: str | None = None
    forbidden_topics: str | None = None
    personalization_answers: dict[str, Any] | None = None
    selected_options: dict[str, Any] | None = None
    project_id: UUID

    model_config = {"from_attributes": True, "populate_by_name": True}

    @property
    def relationship(self) -> str | None:
        return self.relationship_

    @relationship.setter
    def relationship(self, value: str | None) -> None:
        self.relationship_ = value


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


class BriefCompleteResponse(BaseModel):
    project_id: UUID
    status: str
