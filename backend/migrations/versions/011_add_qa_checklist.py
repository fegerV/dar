"""Add qa_checklist to template_versions

Revision ID: 011_add_qa_checklist
Revises: 010_add_scheduled_delivery
Create Date: 2026-08-17

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "011_add_qa_checklist"
down_revision: str | None = "010_add_scheduled_delivery"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("template_versions", sa.Column("qa_checklist", sa.JSON))


def downgrade() -> None:
    op.drop_column("template_versions", "qa_checklist")
