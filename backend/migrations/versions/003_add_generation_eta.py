"""Add generation ETA field

Revision ID: 003_add_generation_eta
Revises: 002_add_generation_progress
Create Date: 2026-08-17

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "003_add_generation_eta"
down_revision: str | None = "002_add_generation_progress"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("generations", sa.Column("estimated_seconds", sa.Integer))


def downgrade() -> None:
    op.drop_column("generations", "estimated_seconds")
