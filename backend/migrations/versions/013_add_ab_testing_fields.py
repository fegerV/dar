"""Add A/B testing fields to template_versions

Revision ID: 013_add_ab_testing_fields
Revises: 012_create_feedback
Create Date: 2026-08-17

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "013_add_ab_testing_fields"
down_revision: str | None = "012_create_feedback"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("template_versions", sa.Column("variant_group", sa.String(100)))
    op.add_column("template_versions", sa.Column("variant_name", sa.String(100)))


def downgrade() -> None:
    op.drop_column("template_versions", "variant_name")
    op.drop_column("template_versions", "variant_group")
