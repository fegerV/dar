"""Add gift fulfillment fields to deliveries

Revision ID: 014_add_gift_fulfillment
Revises: 013_add_ab_testing_fields
Create Date: 2026-08-17

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "014_add_gift_fulfillment"
down_revision: str | None = "013_add_ab_testing_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("deliveries", sa.Column("gift_fulfillment_status", sa.String(30)))


def downgrade() -> None:
    op.drop_column("deliveries", "gift_fulfillment_status")
