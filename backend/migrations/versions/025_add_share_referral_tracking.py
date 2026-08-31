"""Add referral tracking fields to delivery_links

Revision ID: 025_add_share_referral_tracking
Revises: 024_add_ab_testing
Create Date: 2026-08-19

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "025_add_share_referral_tracking"
down_revision: str | None = "024_add_ab_testing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("delivery_links", sa.Column("referral_code", sa.String(50), nullable=True))
    op.add_column("delivery_links", sa.Column("referrer_user_id", sa.UUID(as_uuid=True), nullable=True))
    op.add_column("delivery_links", sa.Column("referral_attribution_count", sa.Integer, nullable=False, default=0))
    op.create_index("ix_delivery_links_referral_code", "delivery_links", ["referral_code"])


def downgrade() -> None:
    op.drop_index("ix_delivery_links_referral_code", table_name="delivery_links")
    op.drop_column("delivery_links", "referral_attribution_count")
    op.drop_column("delivery_links", "referrer_user_id")
    op.drop_column("delivery_links", "referral_code")
