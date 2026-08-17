import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class Recommendation(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "recommendations"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    template_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="generated")
    rank: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    score: Mapped[float | None] = mapped_column(Numeric(8, 4))
    match_reasons: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    explanation: Mapped[str | None] = mapped_column(Text)
    generated_by_model: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    selected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
