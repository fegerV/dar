"""UUID-first SQLAlchemy models for the backend-first MVP."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def now_column() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), default=datetime.utcnow)


def json_default(default):
    return mapped_column(JSON, default=default)


class User(Base):
    __tablename__ = "users"

    id = uuid_pk()
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    locale: Mapped[str] = mapped_column(String(16), default="ru-RU")
    timezone: Mapped[str] = mapped_column(String(64), default="Europe/Moscow")
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at = now_column()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    wallet: Mapped["Wallet"] = relationship(back_populates="user", cascade="all, delete-orphan")


class AuthAccount(Base):
    __tablename__ = "auth_accounts"
    __table_args__ = (UniqueConstraint("provider", "provider_user_id", name="ux_auth_provider_user"),)

    id = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(32), default="email")
    provider_user_id: Mapped[str] = mapped_column(String(320))
    created_at = now_column()


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at = now_column()


class Recipient(Base):
    __tablename__ = "recipients"

    id = uuid_pk()
    owner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(32), nullable=True)
    birth_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    relationship_type: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    relationship_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    interests: Mapped[list] = json_default(list)
    traits: Mapped[list] = json_default(list)
    forbidden_topics: Mapped[list] = json_default(list)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = now_column()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"

    id = uuid_pk()
    owner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    recipient_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("recipients.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    occasion_code: Mapped[str] = mapped_column(String(64), index=True)
    occasion_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    selected_recommendation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    selected_template_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    master_frame_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True)
    final_generation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    price_rub: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    paid_rub: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    metadata_json: Mapped[dict] = json_default(dict)
    created_at = now_column()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    brief: Mapped["CreativeBrief"] = relationship(back_populates="project", cascade="all, delete-orphan")
    master_frame: Mapped["Asset"] = relationship("Asset")


class CreativeBrief(Base):
    __tablename__ = "creative_briefs"

    id = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    relationship_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    desired_mood: Mapped[str | None] = mapped_column(String(64), nullable=True)
    desired_length_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    humor_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    emotion_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    surprise_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    personalization_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    inside_joke: Mapped[str | None] = mapped_column(Text, nullable=True)
    hobbies_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    character_traits: Mapped[str | None] = mapped_column(Text, nullable=True)
    memorable_story: Mapped[str | None] = mapped_column(Text, nullable=True)
    desired_phrase: Mapped[str | None] = mapped_column(Text, nullable=True)
    forbidden_topics: Mapped[str | None] = mapped_column(Text, nullable=True)
    sender_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected_options: Mapped[dict] = json_default(dict)
    created_at = now_column()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    project: Mapped[Project] = relationship(back_populates="brief")


class Template(Base):
    __tablename__ = "templates"

    id = uuid_pk()
    code: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    kind: Mapped[str] = mapped_column(String(32), default="video")
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    occasion_codes: Mapped[list] = json_default(list)
    relationship_types: Mapped[list] = json_default(list)
    moods: Mapped[list] = json_default(list)
    base_price_rub: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("590"))
    metadata_json: Mapped[dict] = json_default(dict)
    created_at = now_column()

    versions: Mapped[list["TemplateVersion"]] = relationship(back_populates="template", cascade="all, delete-orphan")


class TemplateVersion(Base):
    __tablename__ = "template_versions"
    __table_args__ = (UniqueConstraint("template_id", "version", name="ux_template_version"),)

    id = uuid_pk()
    template_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("templates.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    prompt_config: Mapped[dict] = json_default(dict)
    render_config: Mapped[dict] = json_default(dict)
    personalization_config: Mapped[dict] = json_default(dict)
    validation_config: Mapped[dict] = json_default(dict)
    created_at = now_column()

    template: Mapped[Template] = relationship(back_populates="versions")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    template_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("template_versions.id", ondelete="RESTRICT"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="generated")
    rank: Mapped[int] = mapped_column(Integer)
    score: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=Decimal("0"))
    match_reasons: Mapped[list] = json_default(list)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = now_column()


class StorageObject(Base):
    __tablename__ = "storage_objects"

    id = uuid_pk()
    bucket: Mapped[str] = mapped_column(String(128))
    object_key: Mapped[str] = mapped_column(String(512))
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_provider: Mapped[str] = mapped_column(String(32), default="minio")
    metadata_json: Mapped[dict] = json_default(dict)
    created_at = now_column()


class Asset(Base):
    __tablename__ = "assets"

    id = uuid_pk()
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    type: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(32), default="ready")
    storage_object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("storage_objects.id", ondelete="RESTRICT"))
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    duration_sec: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = json_default(dict)
    created_at = now_column()


class ProjectAsset(Base):
    __tablename__ = "project_assets"
    __table_args__ = (UniqueConstraint("project_id", "asset_id", "role", name="ux_project_asset_role"),)

    id = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), index=True)
    role: Mapped[str] = mapped_column(String(64))
    created_at = now_column()


class Wallet(Base):
    __tablename__ = "wallets"

    id = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    balance_rub: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    bonus_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="wallet")


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = uuid_pk()
    wallet_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("wallets.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="completed")
    amount_rub: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    bonus_amount_rub: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    balance_after_rub: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    payment_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = now_column()


class Entitlement(Base):
    __tablename__ = "entitlements"

    id = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    consumed: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at = now_column()


class Payment(Base):
    __tablename__ = "payments"

    id = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    provider: Mapped[str] = mapped_column(String(32), default="mock")
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    method: Mapped[str] = mapped_column(String(32), default="mock")
    amount_rub: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    external_payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    provider_payload: Mapped[dict] = json_default(dict)
    confirmation_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at = now_column()
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Generation(Base):
    __tablename__ = "generations"

    id = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    template_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("template_versions.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[str] = mapped_column(String(32), default="final")
    status: Mapped[str] = mapped_column(String(32), default="created", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    current_step: Mapped[str | None] = mapped_column(String(64), nullable=True)
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    input_json: Mapped[dict] = json_default(dict)
    output_json: Mapped[dict] = json_default(dict)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost_rub: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("0"))
    created_at = now_column()
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class GenerationStep(Base):
    __tablename__ = "generation_steps"

    id = uuid_pk()
    generation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generations.id", ondelete="CASCADE"), index=True)
    step_no: Mapped[int] = mapped_column(Integer)
    step_code: Mapped[str] = mapped_column(String(64))
    type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="created")
    input_json: Mapped[dict] = json_default(dict)
    output_json: Mapped[dict] = json_default(dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = now_column()
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class GenerationOutput(Base):
    __tablename__ = "generation_outputs"

    id = uuid_pk()
    generation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generations.id", ondelete="CASCADE"), index=True)
    asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), index=True)
    role: Mapped[str] = mapped_column(String(64))
    created_at = now_column()


class DeliveryLink(Base):
    __tablename__ = "delivery_links"

    id = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    generation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("generations.id", ondelete="SET NULL"), nullable=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at = now_column()
    last_opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Delivery(Base):
    __tablename__ = "deliveries"

    id = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    generation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    channel: Mapped[str] = mapped_column(String(32), default="link")
    status: Mapped[str] = mapped_column(String(32), default="created")
    delivery_link_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    destination: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = now_column()


class Feedback(Base):
    __tablename__ = "feedback"

    id = uuid_pk()
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    generation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    reaction: Mapped[str] = mapped_column(String(64))
    categories: Mapped[list] = json_default(list)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = now_column()


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    event_name: Mapped[str] = mapped_column(String(128), index=True)
    platform: Mapped[str | None] = mapped_column(String(32), nullable=True)
    properties: Mapped[dict] = json_default(dict)
    occurred_at = now_column()


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    role: Mapped[str] = mapped_column(String(64), default="admin")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at = now_column()
