import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "projects"

    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    recipient_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipients.id", ondelete="SET NULL")
    )
    title: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="private")
    occasion_code: Mapped[str | None] = mapped_column(String(50))
    occasion_title: Mapped[str | None] = mapped_column(Text)
    holiday_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("holidays.id", ondelete="SET NULL"))
    requested_delivery_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    selected_recommendation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    selected_template_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    final_generation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    price_rub: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    bonus_discount_rub: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    promo_discount_rub: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    paid_rub: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    brief = relationship("CreativeBrief", back_populates="project", uselist=False, cascade="all, delete-orphan")
    holiday = relationship("Holiday", uselist=False)
