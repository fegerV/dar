"""
Generation models for tracking AI generation tasks and their states.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Numeric, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class GenerationStatus(str, Enum):
    """Generation task status."""

    QUEUED = "queued"
    PREPARING = "preparing"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    TTS_GENERATION = "tts_generation"
    MUSIC_GENERATION = "music_generation"
    ASSEMBLY = "assembly"
    QUALITY_CHECK = "quality_check"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CreativeBrief(Base):
    """Creative brief - user input for generation."""

    __tablename__ = "creative_briefs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    occasion: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., "birthday"
    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_relation: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g., "friend", "mom"
    sender_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tone: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g., "funny"
    style: Mapped[str | None] = mapped_column(String(100), nullable=True)
    personalization_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_urls: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )  # List of original photo URLs
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    generations: Mapped[list["Generation"]] = relationship(
        "Generation", back_populates="creative_brief", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CreativeBrief(id={self.id}, occasion={self.occasion})>"


class Generation(Base):
    """Main generation task."""

    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    creative_brief_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("creative_briefs.id", ondelete="CASCADE"), nullable=False
    )
    template_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("templates.id"), nullable=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[GenerationStatus] = mapped_column(
        String(50), default=GenerationStatus.QUEUED
    )
    cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    creative_brief: Mapped["CreativeBrief"] = relationship(
        "CreativeBrief", back_populates="generations"
    )
    steps: Mapped[list["GenerationStep"]] = relationship(
        "GenerationStep", back_populates="generation", cascade="all, delete-orphan"
    )
    assets: Mapped[list["GenerationAsset"]] = relationship(
        "GenerationAsset", back_populates="generation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Generation(id={self.id}, status={self.status})>"


class GenerationStep(Base):
    """Individual step in the generation pipeline."""

    __tablename__ = "generation_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    generation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("generations.id", ondelete="CASCADE"), nullable=False
    )
    step_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provider_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    generation: Mapped["Generation"] = relationship(
        "Generation", back_populates="steps"
    )

    def __repr__(self) -> str:
        return f"<GenerationStep(id={self.id}, type={self.step_type})>"


class GenerationAsset(Base):
    """Generated asset (image, video, audio)."""

    __tablename__ = "generation_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    generation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("generations.id", ondelete="CASCADE"), nullable=False
    )
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)
    is_final: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    generation: Mapped["Generation"] = relationship(
        "Generation", back_populates="assets"
    )

    def __repr__(self) -> str:
        return f"<GenerationAsset(id={self.id}, type={self.asset_type})>"
