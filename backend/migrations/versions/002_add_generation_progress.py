"""Add generation progress tracking

Revision ID: 002_add_generation_progress
Revises: 001_initial
Create Date: 2026-08-17

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002_add_generation_progress"
down_revision: str | None = "001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("generations", sa.Column("progress", sa.Integer, nullable=False, server_default="0"))
    op.add_column("generations", sa.Column("current_step", sa.String(50)))


def downgrade() -> None:
    op.drop_column("generations", "current_step")
    op.drop_column("generations", "progress")
