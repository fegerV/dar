import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Role(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    permissions: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class UserRole(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    granted_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AdminUser(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "admin_users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="admin")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class Worker(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "workers"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="idle")
    gpu_model: Mapped[str | None] = mapped_column(String(50))
    gpu_vram_total_gb: Mapped[int | None] = mapped_column(Integer)
    gpu_vram_used_gb: Mapped[int | None] = mapped_column(Integer)
    cpu_usage_percent: Mapped[float | None] = mapped_column(Float)
    jobs_today: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failures_today: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_generation_time_sec: Mapped[float | None] = mapped_column(Float)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class QueueJob(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "queue_jobs"

    generation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generations.id", ondelete="CASCADE"), nullable=False
    )
    worker_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("workers.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_code: Mapped[str | None] = mapped_column(String(50))
    error_message: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class SystemSettings(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    description: Mapped[str | None] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
