"""Create intelligence tables: preflight, recipes, failures, feedback, model_profiles

Revision ID: 016_create_intelligence_tables
Revises: 015_create_quality_tables
Create Date: 2026-08-18

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "016_create_intelligence_tables"
down_revision: str | None = "015_create_quality_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "image_preflight_results",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("generation_id", sa.UUID(as_uuid=True), sa.ForeignKey("generations.id", ondelete="SET NULL")),
        sa.Column("image_url", sa.Text, nullable=False),
        sa.Column("quality_score", sa.Float),
        sa.Column("face_count", sa.Integer),
        sa.Column("face_size", sa.String(20)),
        sa.Column("pose", sa.String(30)),
        sa.Column("sharpness", sa.Float),
        sa.Column("recommended_models", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("recommended_templates", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("issues", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("raw_response", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "video_recipes",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("template_code", sa.String(50), nullable=False),
        sa.Column("model_name", sa.String(50), nullable=False),
        sa.Column("model_version", sa.String(50)),
        sa.Column("prompt", sa.Text),
        sa.Column("negative_strategy", sa.Text),
        sa.Column("duration_sec", sa.Integer),
        sa.Column("camera", sa.String(50)),
        sa.Column("motion", sa.String(50)),
        sa.Column("speech", sa.Integer),
        sa.Column("cost_estimate", sa.Numeric(12, 4)),
        sa.Column("success_rate", sa.Float),
        sa.Column("avg_generations", sa.Float),
        sa.Column("last_tested_at", sa.DateTime(timezone=True)),
        sa.Column("is_active", sa.Integer, nullable=False, server_default=sa.text("1")),
        sa.Column("meta", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_video_recipes_code", "video_recipes", ["code"], unique=True)

    op.create_table(
        "recipe_failures",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("recipe_id", sa.UUID(as_uuid=True), sa.ForeignKey("video_recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("condition", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(20)),
        sa.Column("recommendation", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_recipe_failures_recipe", "recipe_failures", ["recipe_id"])

    op.create_table(
        "generation_failures",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("generation_id", sa.UUID(as_uuid=True), sa.ForeignKey("generations.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("failure_codes", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("repaired_prompt", sa.Text),
        sa.Column("repaired_negative", sa.Text),
        sa.Column("repaired_model", sa.String(50)),
        sa.Column("repaired_template", sa.String(50)),
        sa.Column("attempt", sa.Integer),
        sa.Column("critic_overall", sa.Float),
        sa.Column("critic_decision", sa.String(20)),
        sa.Column("raw_critic", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_generation_failures_generation", "generation_failures", ["generation_id"])

    op.create_table(
        "user_feedback",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("generation_id", sa.UUID(as_uuid=True), sa.ForeignKey("generations.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("rating", sa.String(20)),
        sa.Column("reason", sa.String(50)),
        sa.Column("comment", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_feedback_generation", "user_feedback", ["generation_id"])

    op.create_table(
        "model_profiles",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("model_name", sa.String(50), unique=True, nullable=False),
        sa.Column("provider", sa.String(50)),
        sa.Column("version", sa.String(50)),
        sa.Column("cost_per_sec", sa.Numeric(12, 4)),
        sa.Column("avg_generation_time_sec", sa.Float),
        sa.Column("supports_image_to_video", sa.Integer),
        sa.Column("supports_audio", sa.Integer),
        sa.Column("supports_control", sa.Integer),
        sa.Column("preferred_scenes", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("known_weaknesses", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("meta", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_model_profiles_model_name", "model_profiles", ["model_name"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_model_profiles_model_name", table_name="model_profiles")
    op.drop_table("model_profiles")
    op.drop_index("ix_user_feedback_generation", table_name="user_feedback")
    op.drop_table("user_feedback")
    op.drop_index("ix_generation_failures_generation", table_name="generation_failures")
    op.drop_table("generation_failures")
    op.drop_index("ix_recipe_failures_recipe", table_name="recipe_failures")
    op.drop_table("recipe_failures")
    op.drop_index("ix_video_recipes_code", table_name="video_recipes")
    op.drop_table("video_recipes")
    op.drop_table("image_preflight_results")
