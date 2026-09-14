"""Add missing tables and columns referenced by ORM models

Adds:
  - scenes.sort_order                (drag-and-drop reorder persistence)
  - holidays.sort_order              (Holiday.sort_order)
  - ab_tests.variant_a_id / variant_b_id / results_lock
  - prompt_templates, prompt_template_versions
  - worker_logs

Revision ID: 034_admin_template_fixes
Revises: 033_ai_providers_models
Create Date: 2026-09-14

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

revision: str = "034_admin_template_fixes"
down_revision: str | None = "033_ai_providers_models"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- scenes.sort_order -------------------------------------------------
    op.add_column("scenes", sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"))
    op.create_index("ix_scenes_template_sort_order", "scenes", ["template_id", "sort_order"])

    # --- holidays.sort_order ----------------------------------------------
    op.add_column("holidays", sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"))

    # --- ab_tests variant references + results lock -----------------------
    op.add_column("ab_tests", sa.Column("variant_a_id", UUID(as_uuid=True), nullable=True))
    op.add_column("ab_tests", sa.Column("variant_b_id", UUID(as_uuid=True), nullable=True))
    op.add_column(
        "ab_tests",
        sa.Column("results_lock", sa.Boolean, nullable=False, server_default=sa.text("false")),
    )

    # --- prompt_templates --------------------------------------------------
    op.create_table(
        "prompt_templates",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("name", Text, nullable=False),
        sa.Column("description", Text, nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("text", Text, nullable=False),
        sa.Column("variables", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("compatible_models", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("version", sa.Integer, nullable=False, server_default=sa.text("1")),
        sa.Column("success_rate", sa.Float, nullable=True),
        sa.Column("usage_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("rating", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_prompt_templates_category", "prompt_templates", ["category"])
    op.create_index("ix_prompt_templates_is_active", "prompt_templates", ["is_active"])

    # --- prompt_template_versions -----------------------------------------
    op.create_table(
        "prompt_template_versions",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("prompt_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("name", Text, nullable=False),
        sa.Column("description", Text, nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("text", Text, nullable=False),
        sa.Column("variables", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("compatible_models", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retired_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["prompt_id"], ["prompt_templates.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_ptv_prompt_version",
        "prompt_template_versions",
        ["prompt_id", "version"],
        unique=True,
    )

    # --- worker_logs -------------------------------------------------------
    op.create_table(
        "worker_logs",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("worker_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("level", sa.String(20), nullable=False, server_default="info"),
        sa.Column("message", Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["worker_id"], ["workers.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_worker_logs_worker_created", "worker_logs", ["worker_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_worker_logs_worker_created", table_name="worker_logs")
    op.drop_table("worker_logs")

    op.drop_index("ix_ptv_prompt_version", table_name="prompt_template_versions")
    op.drop_table("prompt_template_versions")

    op.drop_index("ix_prompt_templates_is_active", table_name="prompt_templates")
    op.drop_index("ix_prompt_templates_category", table_name="prompt_templates")
    op.drop_table("prompt_templates")

    op.drop_column("ab_tests", "results_lock")
    op.drop_column("ab_tests", "variant_b_id")
    op.drop_column("ab_tests", "variant_a_id")

    op.drop_column("holidays", "sort_order")

    op.drop_index("ix_scenes_template_sort_order", table_name="scenes")
    op.drop_column("scenes", "sort_order")
