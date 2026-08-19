from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RelationshipSubtypeResponse(BaseModel):
    id: UUID
    code: str
    title: str
    parent_code: str | None = None
    sort_order: int = 0
    is_active: bool = True

    model_config = {"from_attributes": True}


class RecipientGroupBase(BaseModel):
    code: str
    title: str


class RecipientGroupCreate(RecipientGroupBase):
    pass


class RecipientGroupResponse(RecipientGroupBase):
    id: UUID
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class SharedMemoryBase(BaseModel):
    recipient_id: UUID
    title: str = Field(..., max_length=255)
    description: str = Field(..., max_length=2000)
    tags: list[str] = Field(default_factory=list)
    remind_before_days: int | None = None


class SharedMemoryCreate(SharedMemoryBase):
    pass


class SharedMemoryResponse(SharedMemoryBase):
    id: UUID
    group_id: UUID | None = None
    is_active: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class RecipientContext(BaseModel):
    relationship_subtype: str | None = None
    group_id: UUID | None = None
    shared_memories: list[SharedMemoryResponse] = Field(default_factory=list)
    inside_jokes: list[str] = Field(default_factory=list)
