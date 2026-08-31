"""Create gallery tables

Revision ID: 026_create_gallery
Revises: 025_add_share_referral_tracking
Create Date: 2026-08-19

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "026_create_gallery"
down_revision: str | None = "025_add_share_referral_tracking"
branch_labels: str | Sequence[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "gallery_submissions",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("generation_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("thumbnail_url", sa.Text, nullable=True),
        sa.Column("video_url", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, default="pending"),
        sa.Column("is_public", sa.Boolean, nullable=False, default=False),
        sa.Column("consent_given", sa.Boolean, nullable=False, default=False),
        sa.Column("moderator_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["generation_id"], ["generations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_gallery_status", "gallery_submissions", ["status"])
    op.create_index("ix_gallery_user", "gallery_submissions", ["user_id"])
    op.create_index("ix_gallery_public", "gallery_submissions", ["is_public", "status"])


def downgrade() -> None:
    op.drop_index("ix_gallery_public", table_name="gallery_submissions")
    op.drop_index("ix_gallery_user", table_name="gallery_submissions")
    op.drop_index("ix_gallery_status", table_name="gallery_submissions")
    op.drop_table("gallery_submissions")
