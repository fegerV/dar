"""Add last_autosave_at column to creative_briefs

Revision ID: 029_brief_autosave
Revises: 028_registration_fixes
Create Date: 2026-08-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "029_brief_autosave"
down_revision: Union[str, None] = "028_registration_fixes"
branch_labels: Union[str, Sequence[str] | None] = None
depends_on: Union[str, Sequence[str] | None] = None


def upgrade() -> None:
    op.add_column(
        "creative_briefs",
        sa.Column("last_autosave_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_column("creative_briefs", "last_autosave_at")
