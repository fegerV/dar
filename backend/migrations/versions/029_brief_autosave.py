"""Add last_autosave_at column to creative_briefs

Revision ID: 029_brief_autosave
Revises: 028_registration_fixes
Create Date: 2026-08-20

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "029_brief_autosave"
down_revision: str | None = "028_registration_fixes"
branch_labels: str | (Sequence[str] | None) = None
depends_on: str | (Sequence[str] | None) = None


def upgrade() -> None:
    op.add_column(
        "creative_briefs",
        sa.Column("last_autosave_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_column("creative_briefs", "last_autosave_at")
