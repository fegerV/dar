"""Add gift fulfillment fields to deliveries

Revision ID: 014_add_gift_fulfillment
Revises: 013_add_ab_testing_fields
Create Date: 2026-08-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "014_add_gift_fulfillment"
down_revision: Union[str, None] = "013_add_ab_testing_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("deliveries", sa.Column("gift_fulfillment_status", sa.String(30)))


def downgrade() -> None:
    op.drop_column("deliveries", "gift_fulfillment_status")
