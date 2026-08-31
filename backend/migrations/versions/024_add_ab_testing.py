"""Create AB testing tables

Revision ID: 024_add_ab_testing
Revises: 023_add_viewing_reactions
Create Date: 2026-08-19

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "024_add_ab_testing"
down_revision: str | None = "023_add_viewing_reactions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "ab_tests",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("target", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, default="draft"),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("traffic_allocation", sa.Integer, nullable=False, default=100),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "ab_test_variants",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("test_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("config", sa.JSON, nullable=False, default=lambda: {}),
        sa.Column("traffic_weight", sa.Integer, nullable=False, default=50),
        sa.Column("is_control", sa.Boolean, nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["test_id"], ["ab_tests.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("test_id", "code", name="uq_ab_variant_test_code"),
    )

    op.create_table(
        "ab_test_results",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("test_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("variant_code", sa.String(50), nullable=False),
        sa.Column("metric", sa.String(100), nullable=False),
        sa.Column("value", sa.Numeric, nullable=False),
        sa.Column("user_count", sa.Integer, nullable=False, default=0),
        sa.Column("conversion_rate", sa.Numeric, nullable=True),
        sa.Column("revenue_impact_rub", sa.Numeric, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["test_id"], ["ab_tests.id"], ondelete="CASCADE"),
    )

    op.create_index("ix_ab_test_variants_test_id", "ab_test_variants", ["test_id"])
    op.create_index("ix_ab_test_results_test_id", "ab_test_results", ["test_id", "variant_code"])


def downgrade() -> None:
    op.drop_index("ix_ab_test_results_test_id", table_name="ab_test_results")
    op.drop_index("ix_ab_test_variants_test_id", table_name="ab_test_variants")
    op.drop_table("ab_test_results")
    op.drop_table("ab_test_variants")
    op.drop_table("ab_tests")
