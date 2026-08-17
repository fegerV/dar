"""
Template models for managing greeting templates and their versions.
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Numeric, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Template(Base):
    """Greeting template."""

    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    occasion: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    sender_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # who is greeting
    recipient_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # who is being greeted
    style: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    base_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.00)
    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    versions: Mapped[list["TemplateVersion"]] = relationship(
        "TemplateVersion", back_populates="template", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Template(id={self.id}, name={self.name})>"


class TemplateVersion(Base):
    """Template version with prompts and configuration."""

    __tablename__ = "template_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Template structure
    scenes: Mapped[list[dict]] = mapped_column(
        JSON, default=list
    )  # List of scene configurations
    variables: Mapped[list[dict]] = mapped_column(
        JSON, default=list
    )  # Template variables
    conditions: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # AI Prompts
    image_prompts: Mapped[list[dict]] = mapped_column(
        JSON, default=list
    )  # Image generation prompts
    video_prompts: Mapped[list[dict]] = mapped_column(
        JSON, default=list
    )  # Video generation prompts
    tts_script: Mapped[str | None] = mapped_column(Text, nullable=True)
    music_style: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Configuration
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.00)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    # Relationships
    template: Mapped["Template"] = relationship(
        "Template", back_populates="versions"
    )

    def __repr__(self) -> str:
        return f"<TemplateVersion(id={self.id}, template_id={self.template_id}, v{self.version_number})>"


class PromptLibrary(Base):
    """Library of reusable prompts."""

    __tablename__ = "prompt_library"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PromptLibrary(id={self.id}, name={self.name})>"
