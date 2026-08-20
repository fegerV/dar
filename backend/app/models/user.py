import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    display_name: Mapped[str | None] = mapped_column(Text)
    first_name: Mapped[str | None] = mapped_column(Text)
    last_name: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(30))
    avatar_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    locale: Mapped[str] = mapped_column(String(10), nullable=False, default="ru-RU")
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="Europe/Moscow")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    birth_date: Mapped[date | None] = mapped_column(Date)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    telegram_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    auth_identities = relationship("UserAuthIdentity", back_populates="user", cascade="all, delete-orphan")
    wallet = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", backref="user", uselist=False, cascade="all, delete-orphan")


class UserAuthIdentity(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "user_auth_identities"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(30))
    credentials_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user = relationship("User", back_populates="auth_identities")


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    preferred_moods: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    preferred_styles: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    notification_settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    marketing_opt_in: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    analytics_opt_in: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
