"""Create quality_checks and video_critic_results tables

Revision ID: 015_create_quality_tables
Revises: 014_add_gift_fulfillment
Create Date: 2026-08-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "015_create_quality_tables"
down_revision: Union[str, None] = "014_add_gift_fulfillment"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quality_checks",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("generation_id", sa.UUID(as_uuid=True), sa.ForeignKey("generations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step_id", sa.UUID(as_uuid=True), sa.ForeignKey("generation_steps.id", ondelete="SET NULL")),
        sa.Column("check_type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("score", sa.Float),
        sa.Column("details", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_quality_checks_generation", "quality_checks", ["generation_id"])

    op.create_table(
        "video_critic_results",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("generation_id", sa.UUID(as_uuid=True), sa.ForeignKey("generations.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("identity_score", sa.Float),
        sa.Column("motion_score", sa.Float),
        sa.Column("prompt_adherence", sa.Float),
        sa.Column("face_quality", sa.Float),
        sa.Column("artifact_score", sa.Float),
        sa.Column("overall", sa.Float),
        sa.Column("decision", sa.String(20)),
        sa.Column("raw_response", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_video_critic_results_generation", "video_critic_results", ["generation_id"])


def downgrade() -> None:
    op.drop_index("ix_video_critic_results_generation", table_name="video_critic_results")
    op.drop_table("video_critic_results")
    op.drop_index("ix_quality_checks_generation", table_name="quality_checks")
    op.drop_table("quality_checks")
