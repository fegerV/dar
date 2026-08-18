import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class ImagePreflightResult(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "image_preflight_results"

    generation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generations.id", ondelete="SET NULL")
    )
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    quality_score: Mapped[float | None] = mapped_column(Float)
    face_count: Mapped[int | None] = mapped_column(Integer)
    face_size: Mapped[str | None] = mapped_column(String(20))
    pose: Mapped[str | None] = mapped_column(String(30))
    sharpness: Mapped[float | None] = mapped_column(Float)
    recommended_models: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    recommended_templates: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    issues: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    raw_response: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class VideoRecipe(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "video_recipes"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    template_code: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(50))
    prompt: Mapped[str | None] = mapped_column(Text)
    negative_strategy: Mapped[str | None] = mapped_column(Text)
    duration_sec: Mapped[int | None] = mapped_column(Integer)
    camera: Mapped[str | None] = mapped_column(String(50))
    motion: Mapped[str | None] = mapped_column(String(50))
    speech: Mapped[bool | None] = mapped_column(Integer)
    cost_estimate: Mapped[float | None] = mapped_column(Numeric(12, 4))
    success_rate: Mapped[float | None] = mapped_column(Float)
    avg_generations: Mapped[float | None] = mapped_column(Float)
    last_tested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Integer, nullable=False, default=1)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    failures = relationship("RecipeFailure", back_populates="recipe", cascade="all, delete-orphan")


class RecipeFailure(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "recipe_failures"

    recipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("video_recipes.id", ondelete="CASCADE"), nullable=False
    )
    condition: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str | None] = mapped_column(String(20))
    recommendation: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    recipe = relationship("VideoRecipe", back_populates="failures")


class GenerationFailure(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "generation_failures"

    generation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generations.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    failure_codes: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    repaired_prompt: Mapped[str | None] = mapped_column(Text)
    repaired_negative: Mapped[str | None] = mapped_column(Text)
    repaired_model: Mapped[str | None] = mapped_column(String(50))
    repaired_template: Mapped[str | None] = mapped_column(String(50))
    attempt: Mapped[int | None] = mapped_column(Integer)
    critic_overall: Mapped[float | None] = mapped_column(Float)
    critic_decision: Mapped[str | None] = mapped_column(String(20))
    raw_critic: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class UserFeedback(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "user_feedback"

    generation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generations.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    rating: Mapped[str | None] = mapped_column(String(20))
    reason: Mapped[str | None] = mapped_column(String(50))
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ModelProfile(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "model_profiles"

    model_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    provider: Mapped[str | None] = mapped_column(String(50))
    version: Mapped[str | None] = mapped_column(String(50))
    cost_per_sec: Mapped[float | None] = mapped_column(Numeric(12, 4))
    avg_generation_time_sec: Mapped[float | None] = mapped_column(Float)
    supports_image_to_video: Mapped[bool | None] = mapped_column(Integer)
    supports_audio: Mapped[bool | None] = mapped_column(Integer)
    supports_control: Mapped[bool | None] = mapped_column(Integer)
    preferred_scenes: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    known_weaknesses: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
