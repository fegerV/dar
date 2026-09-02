import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Template(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "templates"

    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    category: Mapped[str | None] = mapped_column(String(50))
    occasion_codes: Mapped[list] = mapped_column(ARRAY(String), nullable=False, default=list)
    relationship_types: Mapped[list] = mapped_column(ARRAY(String), nullable=False, default=list)
    moods: Mapped[list] = mapped_column(ARRAY(String), nullable=False, default=list)
    tags: Mapped[list] = mapped_column(ARRAY(String), nullable=False, default=list)
    min_price_rub: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    base_price_rub: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    cost_price_rub: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    estimated_duration_sec: Mapped[int | None] = mapped_column(Integer)
    difficulty: Mapped[int | None] = mapped_column(SmallInteger)
    personalization_score: Mapped[int | None] = mapped_column(SmallInteger)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_rate: Mapped[float | None] = mapped_column(Float)
    avg_rating: Mapped[float | None] = mapped_column(Float)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_rate: Mapped[float | None] = mapped_column(Float)
    preview_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)

    versions = relationship("TemplateVersion", back_populates="template", cascade="all, delete-orphan")
    scenes = relationship("Scene", back_populates="template", cascade="all, delete-orphan")


class TemplateVersion(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "template_versions"

    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    schema_version: Mapped[str] = mapped_column(String(10), nullable=False, default="1.0")
    prompt_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    render_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    personalization_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    validation_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    max_duration_sec: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    qa_checklist: Mapped[dict | None] = mapped_column(JSONB)
    variant_group: Mapped[str | None] = mapped_column(String(100))
    variant_name: Mapped[str | None] = mapped_column(String(100))

    template = relationship("Template", back_populates="versions")
    variables = relationship("TemplateVariable", back_populates="template_version", cascade="all, delete-orphan")


class Scene(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "scenes"

    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    source_title: Mapped[str | None] = mapped_column(Text)
    source_type: Mapped[str | None] = mapped_column(String(30))
    source_reference: Mapped[str | None] = mapped_column(Text)
    rights_status: Mapped[str | None] = mapped_column(String(30))
    duration_sec: Mapped[int | None] = mapped_column(Integer)
    source_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    preview_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    scene_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    condition: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    template = relationship("Template", back_populates="scenes")
    variables = relationship("SceneVariable", back_populates="scene", cascade="all, delete-orphan")


class SceneVariable(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "scene_variables"

    scene_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    variable_type: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    required: Mapped[bool] = mapped_column(nullable=False, default=False)
    default_value: Mapped[dict | None] = mapped_column(JSONB)
    validation_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    options_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    scene = relationship("Scene", back_populates="variables")


class TemplateVariable(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "template_variables"

    template_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("template_versions.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    variable_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_path: Mapped[str | None] = mapped_column(Text)
    required: Mapped[bool] = mapped_column(nullable=False, default=False)
    default_value: Mapped[dict | None] = mapped_column(JSONB)
    validation_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    template_version = relationship("TemplateVersion", back_populates="variables")


class PromptTemplate(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "prompt_templates"

    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(50))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    compatible_models: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    success_rate: Mapped[float | None] = mapped_column(Float)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rating: Mapped[float | None] = mapped_column(Float)
    versions = relationship("PromptTemplateVersion", back_populates="prompt", cascade="all, delete-orphan")


class PromptTemplateVersion(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "prompt_template_versions"

    prompt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prompt_templates.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(50))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    compatible_models: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    prompt = relationship("PromptTemplate", back_populates="versions")
