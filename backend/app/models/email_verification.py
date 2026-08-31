import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class EmailVerification(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "email_verifications"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
