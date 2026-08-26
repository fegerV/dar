import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class LabStatus(PyEnum):
    DRAFT = "draft"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class LabScenario(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "lab_scenarios"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(50))
    difficulty: Mapped[str | None] = mapped_column(String(20))
    prompt_template: Mapped[str | None] = mapped_column(Text)
    negative_strategy: Mapped[str | None] = mapped_column(Text)
    target_duration_sec: Mapped[int | None] = mapped_column(Integer)
    target_camera: Mapped[str | None] = mapped_column(String(50))
    target_motion: Mapped[str | None] = mapped_column(String(50))
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    benchmarks = relationship("LabBenchmark", back_populates="scenario", cascade="all, delete-orphan")


class LabPhoto(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "lab_photos"

    scenario_code: Mapped[str | None] = mapped_column(String(50), ForeignKey("lab_scenarios.code", ondelete="SET NULL"))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str | None] = mapped_column(String(255))
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer)
    mime_type: Mapped[str | None] = mapped_column(String(50))
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    quality_score: Mapped[float | None] = mapped_column(Float)
    face_count: Mapped[int | None] = mapped_column(Integer)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    benchmarks = relationship("LabBenchmark", back_populates="photo")


class LabBenchmark(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "lab_benchmarks"

    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lab_scenarios.id", ondelete="CASCADE"), nullable=False
    )
    photo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lab_photos.id", ondelete="SET NULL")
    )
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=LabStatus.DRAFT.value)
    cost_estimate: Mapped[float | None] = mapped_column(Float)
    actual_cost: Mapped[float | None] = mapped_column(Float)
    generation_time_sec: Mapped[float | None] = mapped_column(Float)
    success_rate: Mapped[float | None] = mapped_column(Float)
    avg_generations: Mapped[float | None] = mapped_column(Float)
    quality_score: Mapped[float | None] = mapped_column(Float)
    output_url: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    raw_result: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    scenario = relationship("LabScenario", back_populates="benchmarks")
    photo = relationship("LabPhoto", back_populates="benchmarks")


class LabRecipeProposal(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "lab_recipe_proposals"

    benchmark_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lab_benchmarks.id", ondelete="CASCADE"), nullable=False
    )
    recipe_code: Mapped[str] = mapped_column(String(50), nullable=False)
    recipe_name: Mapped[str] = mapped_column(String(120), nullable=False)
    template_code: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    auto_generated: Mapped[bool] = mapped_column(Integer, nullable=False, default=1)
    approved: Mapped[bool | None] = mapped_column(Integer)
    approved_by: Mapped[str | None] = mapped_column(String(100))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    applied_to_production: Mapped[bool] = mapped_column(Integer, nullable=False, default=0)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    benchmark = relationship("LabBenchmark")
