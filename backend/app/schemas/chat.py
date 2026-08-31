from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    project_id: str | None = None


class ChatAction(BaseModel):
    type: str
    label: str
    payload: dict = {}


class ChatMessageResponse(BaseModel):
    id: str
    project_id: str
    text: str
    sender: str
    suggestions: list[str] = []
    actions: list[ChatAction] = []
    created_at: datetime


class ProjectCreateRequest(BaseModel):
    recipient_name: str | None = None
    recipient_id: str | None = None
    occasion: str | None = None
    mood: str | None = None


class ProjectResponse(BaseModel):
    id: str
    status: str
    recipient_name: str | None = None
    occasion: str | None = None
    mood: str | None = None
    concept: str | None = None
    text: str | None = None
    created_at: datetime
