import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CreativeBrief(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "creative_briefs"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    occasion_text: Mapped[str | None] = mapped_column(Text)
    sender_role: Mapped[str | None] = mapped_column(Text)
    recipient_role: Mapped[str | None] = mapped_column(Text)
    relationship_: Mapped[str | None] = mapped_column("relationship", String(30))
    relationship_text: Mapped[str | None] = mapped_column(Text)
    desired_mood: Mapped[str | None] = mapped_column(String(30))
    desired_length_sec: Mapped[int | None] = mapped_column(Integer)
    humor_level: Mapped[int | None] = mapped_column(SmallInteger)
    emotion_level: Mapped[int | None] = mapped_column(SmallInteger)
    surprise_level: Mapped[int | None] = mapped_column(SmallInteger)
    personalization_level: Mapped[int | None] = mapped_column(SmallInteger)
    inside_joke: Mapped[str | None] = mapped_column(Text)
    hobbies_text: Mapped[str | None] = mapped_column(Text)
    character_traits: Mapped[str | None] = mapped_column(Text)
    memorable_story: Mapped[str | None] = mapped_column(Text)
    desired_phrase: Mapped[str | None] = mapped_column(Text)
    forbidden_topics: Mapped[str | None] = mapped_column(Text)
    sender_message: Mapped[str | None] = mapped_column(Text)
    personalization_answers: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    selected_options: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    project = relationship("Project", back_populates="brief")

    @property
    def relationship(self) -> str | None:
        return self.relationship_

    @relationship.setter
    def relationship(self, value: str | None) -> None:
        self.relationship_ = value
