"""Add template catalog fields: cost_price, tags, sort_order, metrics

Revision ID: 032_template_catalog_fields
Revises: 031_video_generation_lab
Create Date: 2026-08-26

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "032_template_catalog_fields"
down_revision: str | None = "031_video_generation_lab"
branch_labels: str | Sequence[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("templates", sa.Column("tags", sa.ARRAY(sa.String), nullable=False, server_default="[]"))
    op.add_column("templates", sa.Column("cost_price_rub", sa.Numeric(12, 2), nullable=False, server_default="0"))
    op.add_column("templates", sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"))
    op.add_column("templates", sa.Column("success_rate", sa.Float, nullable=True))
    op.add_column("templates", sa.Column("avg_rating", sa.Float, nullable=True))
    op.add_column("templates", sa.Column("usage_count", sa.Integer, nullable=False, server_default="0"))
    op.add_column("templates", sa.Column("completion_rate", sa.Float, nullable=True))

    op.create_index("ix_templates_category", "templates", ["category"])
    op.create_index("ix_templates_sort_order", "templates", ["sort_order"])


def downgrade() -> None:
    op.drop_index("ix_templates_sort_order", table_name="templates")
    op.drop_index("ix_templates_category", table_name="templates")

    op.drop_column("templates", "completion_rate")
    op.drop_column("templates", "usage_count")
    op.drop_column("templates", "avg_rating")
    op.drop_column("templates", "success_rate")
    op.drop_column("templates", "sort_order")
    op.drop_column("templates", "cost_price_rub")
    op.drop_column("templates", "tags")
