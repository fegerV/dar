import uuid

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class RelationshipType(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "relationship_types"

    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)


class RelationshipSubtype(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "relationship_subtypes"

    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class RecipientGroup(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "recipient_groups"

    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class RecipientSharedMemory(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "recipient_shared_memories"

    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    group_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    remind_before_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
