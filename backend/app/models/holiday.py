import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Holiday(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "holidays"

    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    month: Mapped[int | None] = mapped_column(nullable=True)
    day: Mapped[int | None] = mapped_column(nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(2))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
