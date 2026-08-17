from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True))
    project_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True))
    session_id: Mapped[str | None] = mapped_column(Text)
    event_name: Mapped[str] = mapped_column(String(100), nullable=False)
    event_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    platform: Mapped[str | None] = mapped_column(String(20))
    app_version: Mapped[str | None] = mapped_column(String(20))
    anonymous_id: Mapped[str | None] = mapped_column(Text)
    properties: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
