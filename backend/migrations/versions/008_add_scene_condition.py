"""Add scene condition field

Revision ID: 008_add_scene_condition
Revises: 007_add_holiday_fk_to_projects
Create Date: 2026-08-17

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "008_add_scene_condition"
down_revision: str | None = "007_add_holiday_fk_to_projects"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("scenes", sa.Column("condition", sa.JSON))


def downgrade() -> None:
    op.drop_column("scenes", "condition")
