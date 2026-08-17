"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-08-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("display_name", sa.Text),
        sa.Column("first_name", sa.Text),
        sa.Column("last_name", sa.Text),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(30)),
        sa.Column("avatar_asset_id", UUID(as_uuid=True)),
        sa.Column("locale", sa.String(10), nullable=False, server_default="ru-RU"),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="Europe/Moscow"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="RUB"),
        sa.Column("birth_date", sa.Date),
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_phone", "users", ["phone"])

    # user_auth_identities
    op.create_table(
        "user_auth_identities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("provider_user_id", sa.Text, nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(30)),
        sa.Column("credentials_json", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_user_auth_provider_uid", "user_auth_identities", ["provider", "provider_user_id"], unique=True)

    # user_preferences
    op.create_table(
        "user_preferences",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("preferred_moods", JSONB, nullable=False, server_default="[]"),
        sa.Column("preferred_styles", JSONB, nullable=False, server_default="[]"),
        sa.Column("notification_settings", JSONB, nullable=False, server_default="{}"),
        sa.Column("marketing_opt_in", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("analytics_opt_in", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # recipients
    op.create_table(
        "recipients",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("first_name", sa.Text, nullable=False),
        sa.Column("last_name", sa.Text),
        sa.Column("nickname", sa.Text),
        sa.Column("gender", sa.String(10)),
        sa.Column("birth_date", sa.Date),
        sa.Column("city", sa.Text),
        sa.Column("occupation", sa.Text),
        sa.Column("relationship", sa.String(30)),
        sa.Column("relationship_label", sa.Text),
        sa.Column("contact_phone", sa.String(30)),
        sa.Column("contact_email", sa.String(255)),
        sa.Column("notes", sa.Text),
        sa.Column("interests", JSONB, nullable=False, server_default="[]"),
        sa.Column("traits", JSONB, nullable=False, server_default="[]"),
        sa.Column("favorite_things", JSONB, nullable=False, server_default="[]"),
        sa.Column("forbidden_topics", JSONB, nullable=False, server_default="[]"),
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("archived_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_recipients_owner", "recipients", ["owner_user_id"])

    # recipient_assets
    op.create_table(
        "recipient_assets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("recipient_id", UUID(as_uuid=True), sa.ForeignKey("recipients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_id", UUID(as_uuid=True), nullable=False),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # projects
    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("recipient_id", UUID(as_uuid=True), sa.ForeignKey("recipients.id", ondelete="SET NULL")),
        sa.Column("title", sa.Text),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("visibility", sa.String(20), nullable=False, server_default="private"),
        sa.Column("occasion_code", sa.String(50)),
        sa.Column("occasion_title", sa.Text),
        sa.Column("holiday_id", UUID(as_uuid=True)),
        sa.Column("requested_delivery_at", sa.DateTime(timezone=True)),
        sa.Column("selected_recommendation_id", UUID(as_uuid=True)),
        sa.Column("selected_template_version_id", UUID(as_uuid=True)),
        sa.Column("final_generation_id", UUID(as_uuid=True)),
        sa.Column("price_rub", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("bonus_discount_rub", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("promo_discount_rub", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("paid_rub", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("cancelled_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_projects_owner", "projects", ["owner_user_id"])
    op.create_index("ix_projects_status", "projects", ["status"])

    # creative_briefs
    op.create_table(
        "creative_briefs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("occasion_text", sa.Text),
        sa.Column("sender_role", sa.Text),
        sa.Column("recipient_role", sa.Text),
        sa.Column("relationship", sa.String(30)),
        sa.Column("relationship_text", sa.Text),
        sa.Column("desired_mood", sa.String(30)),
        sa.Column("desired_length_sec", sa.Integer),
        sa.Column("humor_level", sa.SmallInteger),
        sa.Column("emotion_level", sa.SmallInteger),
        sa.Column("surprise_level", sa.SmallInteger),
        sa.Column("personalization_level", sa.SmallInteger),
        sa.Column("inside_joke", sa.Text),
        sa.Column("hobbies_text", sa.Text),
        sa.Column("character_traits", sa.Text),
        sa.Column("memorable_story", sa.Text),
        sa.Column("desired_phrase", sa.Text),
        sa.Column("forbidden_topics", sa.Text),
        sa.Column("sender_message", sa.Text),
        sa.Column("personalization_answers", JSONB, nullable=False, server_default="{}"),
        sa.Column("selected_options", JSONB, nullable=False, server_default="{}"),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # templates
    op.create_table(
        "templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("category", sa.String(50)),
        sa.Column("occasion_codes", ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("relationship_types", ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("moods", ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("min_price_rub", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("base_price_rub", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("estimated_duration_sec", sa.Integer),
        sa.Column("difficulty", sa.SmallInteger),
        sa.Column("personalization_score", sa.SmallInteger),
        sa.Column("preview_asset_id", UUID(as_uuid=True)),
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # template_versions
    op.create_table(
        "template_versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("template_id", UUID(as_uuid=True), sa.ForeignKey("templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("schema_version", sa.String(10), nullable=False, server_default="1.0"),
        sa.Column("prompt_config", JSONB, nullable=False, server_default="{}"),
        sa.Column("render_config", JSONB, nullable=False, server_default="{}"),
        sa.Column("personalization_config", JSONB, nullable=False, server_default="{}"),
        sa.Column("validation_config", JSONB, nullable=False, server_default="{}"),
        sa.Column("max_duration_sec", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("retired_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_tv_template_version", "template_versions", ["template_id", "version"], unique=True)

    # scenes
    op.create_table(
        "scenes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("template_id", UUID(as_uuid=True), sa.ForeignKey("templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("source_title", sa.Text),
        sa.Column("source_type", sa.String(30)),
        sa.Column("source_reference", sa.Text),
        sa.Column("rights_status", sa.String(30)),
        sa.Column("duration_sec", sa.Integer),
        sa.Column("source_asset_id", UUID(as_uuid=True)),
        sa.Column("preview_asset_id", UUID(as_uuid=True)),
        sa.Column("scene_config", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_scenes_template_code", "scenes", ["template_id", "code"], unique=True)

    # scene_variables
    op.create_table(
        "scene_variables",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("scene_id", UUID(as_uuid=True), sa.ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("variable_type", sa.String(30), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("required", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("default_value", JSONB),
        sa.Column("validation_json", JSONB, nullable=False, server_default="{}"),
        sa.Column("options_json", JSONB, nullable=False, server_default="[]"),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
    )

    # template_variables
    op.create_table(
        "template_variables",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("template_version_id", UUID(as_uuid=True), sa.ForeignKey("template_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("variable_type", sa.String(30), nullable=False),
        sa.Column("source_path", sa.Text),
        sa.Column("required", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("default_value", JSONB),
        sa.Column("validation_json", JSONB, nullable=False, server_default="{}"),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
    )

    # generations
    op.create_table(
        "generations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_generation_id", UUID(as_uuid=True), sa.ForeignKey("generations.id", ondelete="SET NULL")),
        sa.Column("template_version_id", UUID(as_uuid=True)),
        sa.Column("type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="created"),
        sa.Column("attempt", sa.Integer, nullable=False, server_default="1"),
        sa.Column("requested_by_user_id", UUID(as_uuid=True)),
        sa.Column("provider_id", UUID(as_uuid=True)),
        sa.Column("model_name", sa.Text),
        sa.Column("input_json", JSONB, nullable=False, server_default="{}"),
        sa.Column("output_json", JSONB, nullable=False, server_default="{}"),
        sa.Column("error_code", sa.Text),
        sa.Column("error_message", sa.Text),
        sa.Column("cost_rub", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("duration_ms", sa.BigInteger),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_generations_project", "generations", ["project_id"])

    # generation_steps
    op.create_table(
        "generation_steps",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("generation_id", UUID(as_uuid=True), sa.ForeignKey("generations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step_no", sa.Integer, nullable=False),
        sa.Column("step_code", sa.String(50), nullable=False),
        sa.Column("type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="created"),
        sa.Column("provider_id", UUID(as_uuid=True)),
        sa.Column("prompt_template_id", UUID(as_uuid=True)),
        sa.Column("input_json", JSONB, nullable=False, server_default="{}"),
        sa.Column("output_json", JSONB, nullable=False, server_default="{}"),
        sa.Column("error_code", sa.Text),
        sa.Column("error_message", sa.Text),
        sa.Column("cost_rub", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("duration_ms", sa.BigInteger),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # generation_jobs
    op.create_table(
        "generation_jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("generation_id", UUID(as_uuid=True), sa.ForeignKey("generations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("generation_step_id", UUID(as_uuid=True)),
        sa.Column("queue_name", sa.String(50), nullable=False, server_default="default"),
        sa.Column("status", sa.String(20), nullable=False, server_default="queued"),
        sa.Column("priority", sa.Integer, nullable=False, server_default="100"),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer, nullable=False, server_default="3"),
        sa.Column("available_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("locked_at", sa.DateTime(timezone=True)),
        sa.Column("locked_by", sa.Text),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("last_error", sa.Text),
        sa.Column("payload", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # wallets
    op.create_table(
        "wallets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("balance_rub", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("bonus_balance", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # payments
    op.create_table(
        "payments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="SET NULL")),
        sa.Column("provider_id", UUID(as_uuid=True)),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("method", sa.String(20), nullable=False),
        sa.Column("amount_rub", sa.Numeric(12, 2), nullable=False),
        sa.Column("bonus_amount_rub", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("discount_rub", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("external_payment_id", sa.Text),
        sa.Column("idempotency_key", sa.Text),
        sa.Column("receipt_json", JSONB),
        sa.Column("provider_payload", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True)),
        sa.Column("refunded_at", sa.DateTime(timezone=True)),
    )

    # entitlements
    op.create_table(
        "entitlements",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="1"),
        sa.Column("consumed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("source", sa.Text),
        sa.Column("source_reference", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # storage_objects
    op.create_table(
        "storage_objects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("bucket", sa.String(100), nullable=False),
        sa.Column("object_key", sa.Text, nullable=False),
        sa.Column("original_name", sa.Text),
        sa.Column("mime_type", sa.String(100)),
        sa.Column("size_bytes", sa.BigInteger),
        sa.Column("sha256", sa.String(64)),
        sa.Column("width", sa.Integer),
        sa.Column("height", sa.Integer),
        sa.Column("duration_ms", sa.BigInteger),
        sa.Column("storage_provider", sa.String(30), nullable=False, server_default="minio"),
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # assets
    op.create_table(
        "assets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_user_id", UUID(as_uuid=True)),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="uploaded"),
        sa.Column("storage_object_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text),
        sa.Column("description", sa.Text),
        sa.Column("duration_sec", sa.Numeric(10, 3)),
        sa.Column("width", sa.Integer),
        sa.Column("height", sa.Integer),
        sa.Column("mime_type", sa.String(100)),
        sa.Column("checksum", sa.String(64)),
        sa.Column("is_private", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("moderation_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # recommendations
    op.create_table(
        "recommendations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("template_version_id", UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="generated"),
        sa.Column("rank", sa.SmallInteger, nullable=False),
        sa.Column("score", sa.Numeric(8, 4)),
        sa.Column("match_reasons", JSONB, nullable=False, server_default="[]"),
        sa.Column("explanation", sa.Text),
        sa.Column("generated_by_model", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("selected_at", sa.DateTime(timezone=True)),
    )

    # delivery_links
    op.create_table(
        "delivery_links",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("generation_id", UUID(as_uuid=True)),
        sa.Column("token_hash", sa.Text, nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("max_views", sa.Integer),
        sa.Column("view_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("password_hash", sa.Text),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_opened_at", sa.DateTime(timezone=True)),
    )

    # deliveries
    op.create_table(
        "deliveries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("generation_id", UUID(as_uuid=True)),
        sa.Column("user_id", UUID(as_uuid=True)),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="created"),
        sa.Column("destination", sa.Text),
        sa.Column("delivery_link_id", UUID(as_uuid=True)),
        sa.Column("external_message_id", sa.Text),
        sa.Column("payload", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("opened_at", sa.DateTime(timezone=True)),
        sa.Column("failed_at", sa.DateTime(timezone=True)),
        sa.Column("error_message", sa.Text),
    )

    # share_events
    op.create_table(
        "share_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("generation_id", UUID(as_uuid=True)),
        sa.Column("user_id", UUID(as_uuid=True)),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("referral_code", sa.Text),
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # analytics_events
    op.create_table(
        "analytics_events",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("user_id", UUID(as_uuid=True)),
        sa.Column("project_id", UUID(as_uuid=True)),
        sa.Column("session_id", sa.Text),
        sa.Column("event_name", sa.String(100), nullable=False),
        sa.Column("event_version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("platform", sa.String(20)),
        sa.Column("app_version", sa.String(20)),
        sa.Column("anonymous_id", sa.Text),
        sa.Column("properties", JSONB, nullable=False, server_default="{}"),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_analytics_event_name", "analytics_events", ["event_name"])
    op.create_index("ix_analytics_occurred", "analytics_events", ["occurred_at"])


def downgrade() -> None:
    op.drop_table("analytics_events")
    op.drop_table("share_events")
    op.drop_table("deliveries")
    op.drop_table("delivery_links")
    op.drop_table("recommendations")
    op.drop_table("assets")
    op.drop_table("storage_objects")
    op.drop_table("entitlements")
    op.drop_table("payments")
    op.drop_table("wallets")
    op.drop_table("generation_jobs")
    op.drop_table("generation_steps")
    op.drop_table("generations")
    op.drop_table("template_variables")
    op.drop_table("scene_variables")
    op.drop_table("scenes")
    op.drop_table("template_versions")
    op.drop_table("templates")
    op.drop_table("creative_briefs")
    op.drop_table("projects")
    op.drop_table("recipient_assets")
    op.drop_table("recipients")
    op.drop_table("user_preferences")
    op.drop_table("user_auth_identities")
    op.drop_table("users")
