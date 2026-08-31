"""Create AI Providers and Models tables

Revision ID: 033_ai_providers_models
Revises: 032_template_catalog_fields
Create Date: 2026-08-26

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "033_ai_providers_models"
down_revision: str | None = "032_template_catalog_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "ai_providers",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("provider_type", sa.String(30), nullable=False),
        sa.Column("base_url", sa.String(500), nullable=False, server_default="https://polza.ai/api/v1"),
        sa.Column("api_key", sa.Text, nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("priority", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("default_model", sa.String(100), nullable=True),
        sa.Column("config", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("meta", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("last_tested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_test_status", sa.String(20), nullable=True),
        sa.Column("last_test_message", Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "ai_models",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("provider_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("model_type", sa.String(30), nullable=False),
        sa.Column("model_id", sa.String(100), nullable=False),
        sa.Column("max_prompt_length", sa.Integer, nullable=False, server_default=sa.text("4096")),
        sa.Column("supports_images", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("supports_video", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("supports_audio", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("default_parameters", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("cost_per_unit", sa.Float, nullable=False, server_default=sa.text("0")),
        sa.Column("unit_type", sa.String(20), nullable=False, server_default="token"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("config", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["provider_id"], ["ai_providers.id"], ondelete="CASCADE"),
    )

    op.create_index("ix_ai_models_provider_id", "ai_models", ["provider_id"])
    op.create_index("ix_ai_models_model_type", "ai_models", ["model_type"])
    op.create_index("ix_ai_models_is_default", "ai_models", ["is_default"])

    op.execute("""
        INSERT INTO ai_providers (name, provider_type, base_url, api_key, enabled, priority, default_model, config)
        VALUES ('Polza AI', 'polza', 'https://polza.ai/api/v1', 'YOUR_POLZA_API_KEY', false, 0, NULL, '{}')
        ON CONFLICT DO NOTHING
    """)

    op.execute("""
        INSERT INTO ai_models (provider_id, name, display_name, model_type, model_id, max_prompt_length, supports_images, supports_video, supports_audio, default_parameters, cost_per_unit, unit_type, enabled, is_default, config)
        SELECT
            p.id,
            'gpt-5-2',
            'ChatGPT 5.2',
            'chat',
            'openai/gpt-5-2',
            128000,
            false,
            false,
            false,
            '{"temperature": 0.7}'::jsonb,
            0.003,
            'token',
            true,
            true,
            '{}'::jsonb
        FROM ai_providers p WHERE p.name = 'Polza AI'
        ON CONFLICT DO NOTHING
    """)

    op.execute("""
        INSERT INTO ai_models (provider_id, name, display_name, model_type, model_id, max_prompt_length, supports_images, supports_video, supports_audio, default_parameters, cost_per_unit, unit_type, enabled, is_default, config)
        SELECT
            p.id,
            'gpt-5-4-image-2',
            'GPT-5.4 Image 2',
            'image',
            'openai/gpt-5-4-image-2',
            20000,
            true,
            false,
            false,
            '{"aspect_ratio": "auto", "image_resolution": "1K"}'::jsonb,
            0.04,
            'image',
            true,
            false,
            '{"aspect_ratios": ["auto", "1:1", "9:16", "16:9", "4:3", "3:4"], "resolutions": ["1K", "2K", "4K"], "max_images": 16}'::jsonb
        FROM ai_providers p WHERE p.name = 'Polza AI'
        ON CONFLICT DO NOTHING
    """)

    op.execute("""
        INSERT INTO ai_models (provider_id, name, display_name, model_type, model_id, max_prompt_length, supports_images, supports_video, supports_audio, default_parameters, cost_per_unit, unit_type, enabled, is_default, config)
        SELECT
            p.id,
            'grok-imagine-video-1-5',
            'Grok Imagine Video 1.5',
            'video_lite',
            'grok-imagine-video-1-5',
            4096,
            true,
            true,
            false,
            '{"aspect_ratio": "auto", "duration": 8, "resolution": "480p"}'::jsonb,
            0.05,
            'second',
            true,
            true,
            '{"aspect_ratios": ["1:1", "16:9", "9:16", "3:2", "2:3", "auto"], "durations": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], "resolutions": ["480p", "720p"], "max_images": 7}'::jsonb
        FROM ai_providers p WHERE p.name = 'Polza AI'
        ON CONFLICT DO NOTHING
    """)

    op.execute("""
        INSERT INTO ai_models (provider_id, name, display_name, model_type, model_id, max_prompt_length, supports_images, supports_video, supports_audio, default_parameters, cost_per_unit, unit_type, enabled, is_default, config)
        SELECT
            p.id,
            'seedance-2-5',
            'Seedance 2.5',
            'video_premium',
            'bytedance/seedance-2-5',
            30000,
            true,
            true,
            true,
            '{"aspect_ratio": "auto", "duration": 5, "generate_audio": "true", "resolution": "720p"}'::jsonb,
            0.08,
            'second',
            true,
            true,
            '{"aspect_ratios": ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "auto"], "durations": [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30], "resolutions": ["480p", "720p"], "max_images": 30, "max_videos": 10}'::jsonb
        FROM ai_providers p WHERE p.name = 'Polza AI'
        ON CONFLICT DO NOTHING
    """)

    op.execute("""
        INSERT INTO ai_models (provider_id, name, display_name, model_type, model_id, max_prompt_length, supports_images, supports_video, supports_audio, default_parameters, cost_per_unit, unit_type, enabled, is_default, config)
        SELECT
            p.id,
            'kling-v2-5',
            'Kling 2.5',
            'video_premium',
            'kling/kling-v2-5',
            4096,
            true,
            true,
            false,
            '{"aspect_ratio": "16:9", "duration": 5}'::jsonb,
            0.06,
            'second',
            true,
            false,
            '{"aspect_ratios": ["16:9", "9:16", "1:1", "4:3", "3:4"], "durations": [5, 10]}'::jsonb
        FROM ai_providers p WHERE p.name = 'Polza AI'
        ON CONFLICT DO NOTHING
    """)

    op.execute("""
        INSERT INTO ai_models (provider_id, name, display_name, model_type, model_id, max_prompt_length, supports_images, supports_video, supports_audio, default_parameters, cost_per_unit, unit_type, enabled, is_default, config)
        SELECT
            p.id,
            'minimax-h3',
            'MiniMax H3',
            'video_premium',
            'minimax/h3',
            4096,
            true,
            true,
            false,
            '{"aspect_ratio": "16:9", "duration": 6}'::jsonb,
            0.05,
            'second',
            true,
            false,
            '{"aspect_ratios": ["16:9", "9:16", "1:1"], "durations": [4, 5, 6, 7, 8]}'::jsonb
        FROM ai_providers p WHERE p.name = 'Polza AI'
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.drop_index("ix_ai_models_is_default", table_name="ai_models")
    op.drop_index("ix_ai_models_model_type", table_name="ai_models")
    op.drop_index("ix_ai_models_provider_id", table_name="ai_models")
    op.drop_table("ai_models")
    op.drop_table("ai_providers")
