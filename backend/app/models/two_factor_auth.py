import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TwoFactorAuth(Base):
    """Модель для двухфакторной аутентификации TOTP."""
    
    __tablename__ = "two_factor_auth"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    totp_secret: Mapped[str] = mapped_column(String(64), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    backup_codes: Mapped[list] = mapped_column(
        Text, nullable=False, default=list, 
        comment="JSON array of hashed backup codes"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    user = relationship("User", backref="two_factor_auth")
