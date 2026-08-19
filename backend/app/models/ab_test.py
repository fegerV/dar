import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ABTest(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ab_tests"

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    target: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    traffic_allocation: Mapped[float] = mapped_column(Integer, nullable=False, default=100)
    variant_a_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    variant_b_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    results_lock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    variants = relationship("ABTestVariant", back_populates="test", cascade="all, delete-orphan")


class ABTestVariant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ab_test_variants"

    test_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ab_tests.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    traffic_weight: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    is_control: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    test = relationship("ABTest", back_populates="variants")


class ABTestResult(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ab_test_results"

    test_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ab_tests.id", ondelete="CASCADE"), nullable=False
    )
    variant_code: Mapped[str] = mapped_column(String(50), nullable=False)
    metric: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[float] = mapped_column(Integer, nullable=False)
    user_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    conversion_rate: Mapped[float | None] = mapped_column(Integer)
    revenue_impact_rub: Mapped[float | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
