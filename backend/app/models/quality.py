import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class QualityCheck(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "quality_checks"

    generation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generations.id", ondelete="CASCADE"), nullable=False
    )
    step_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("generation_steps.id", ondelete="SET NULL"))
    check_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    score: Mapped[float | None] = mapped_column(Float)
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class VideoCriticResult(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "video_critic_results"

    generation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generations.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    identity_score: Mapped[float | None] = mapped_column(Float)
    motion_score: Mapped[float | None] = mapped_column(Float)
    prompt_adherence: Mapped[float | None] = mapped_column(Float)
    face_quality: Mapped[float | None] = mapped_column(Float)
    artifact_score: Mapped[float | None] = mapped_column(Float)
    overall: Mapped[float | None] = mapped_column(Float)
    decision: Mapped[str | None] = mapped_column(String(20))
    raw_response: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
