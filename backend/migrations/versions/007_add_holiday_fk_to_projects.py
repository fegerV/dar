"""Add holidays FK to projects

Revision ID: 007_add_holiday_fk_to_projects
Revises: 006_create_relationship_types
Create Date: 2026-08-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007_add_holiday_fk_to_projects"
down_revision: Union[str, None] = "006_create_relationship_types"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key(
        "fk_projects_holiday",
        "projects",
        "holidays",
        ["holiday_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_projects_holiday", "projects", type_="foreignkey")
