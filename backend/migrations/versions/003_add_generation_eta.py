"""Add generation ETA field

Revision ID: 003_add_generation_eta
Revises: 002_add_generation_progress
Create Date: 2026-08-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_add_generation_eta"
down_revision: Union[str, None] = "002_add_generation_progress"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("generations", sa.Column("estimated_seconds", sa.Integer))


def downgrade() -> None:
    op.drop_column("generations", "estimated_seconds")
