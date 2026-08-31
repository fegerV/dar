"""Add scheduled_at to deliveries

Revision ID: 010_add_scheduled_delivery
Revises: 009_create_referrals
Create Date: 2026-08-17

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "010_add_scheduled_delivery"
down_revision: str | None = "009_create_referrals"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("deliveries", sa.Column("scheduled_at", sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column("deliveries", "scheduled_at")
