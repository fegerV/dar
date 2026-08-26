"""Add Video Generation Lab tables

Revision ID: 031_video_generation_lab
Revises: 030_create_ledger_transactions
Create Date: 2026-08-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op

revision: str = "031_video_generation_lab"
down_revision: Union[str, None] = "030_create_ledger_transactions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table(
        "lab_scenarios",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("difficulty", sa.String(20), nullable=True),
        sa.Column("prompt_template", sa.Text, nullable=True),
        sa.Column("negative_strategy", sa.Text, nullable=True),
        sa.Column("target_duration_sec", sa.Integer, nullable=True),
        sa.Column("target_camera", sa.String(50), nullable=True),
        sa.Column("target_motion", sa.String(50), nullable=True),
        sa.Column("tags", JSONB, nullable=False, server_default="[]"),
        sa.Column("meta", JSONB, nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("code", name="uq_lab_scenarios_code"),
    )

    op.create_table(
        "lab_photos",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("scenario_code", sa.String(50), nullable=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("original_name", sa.String(255), nullable=True),
        sa.Column("file_url", sa.Text, nullable=False),
        sa.Column("file_size_bytes", sa.Integer, nullable=True),
        sa.Column("mime_type", sa.String(50), nullable=True),
        sa.Column("width", sa.Integer, nullable=True),
        sa.Column("height", sa.Integer, nullable=True),
        sa.Column("quality_score", sa.Float, nullable=True),
        sa.Column("face_count", sa.Integer, nullable=True),
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "lab_benchmarks",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("scenario_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("photo_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("model_name", sa.String(50), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("cost_estimate", sa.Float, nullable=True),
        sa.Column("actual_cost", sa.Float, nullable=True),
        sa.Column("generation_time_sec", sa.Float, nullable=True),
        sa.Column("success_rate", sa.Float, nullable=True),
        sa.Column("avg_generations", sa.Float, nullable=True),
        sa.Column("quality_score", sa.Float, nullable=True),
        sa.Column("output_url", sa.Text, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("raw_result", JSONB, nullable=False, server_default="{}"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["scenario_id"], ["lab_scenarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["photo_id"], ["lab_photos.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "lab_recipe_proposals",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("benchmark_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("recipe_code", sa.String(50), nullable=False),
        sa.Column("recipe_name", sa.String(120), nullable=False),
        sa.Column("template_code", sa.String(50), nullable=False),
        sa.Column("model_name", sa.String(50), nullable=False),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("auto_generated", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("approved", sa.Boolean, nullable=True),
        sa.Column("approved_by", sa.String(100), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("applied_to_production", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["benchmark_id"], ["lab_benchmarks.id"], ondelete="CASCADE"),
    )

    op.execute("""
        INSERT INTO lab_scenarios (code, name, description, category, difficulty, prompt_template, target_duration_sec, target_camera, target_motion, tags)
        VALUES
          ('portrait_subtle','Portrait Subtle Motion','Gentle breathing and eye movement for static portraits','portrait','easy','{subject} with subtle natural breathing, gentle eye movement, soft lighting',5,'static','subtle','["portrait","people","subtle"]'),
          ('portrait_talking','Portrait Talking','Lipsync and natural talking motion with gestures','portrait','medium','{subject} talking naturally, lips moving in sync, slight head nods, engaged expression',8,'static','medium','["portrait","people","talking","lipsync"]'),
          ('portrait_emotional','Portrait Emotional','Strong emotional expression with dramatic motion','portrait','hard','{subject} expressing strong emotion, dramatic facial movement, cinematic lighting, intense moment',5,'static','dramatic','["portrait","people","emotion","dramatic"]'),
          ('product_showcase','Product Showcase','360-degree rotation and feature highlights for products','product','medium','{product} rotating smoothly, premium product showcase, studio lighting, feature highlights',8,'orbit','medium','["product","showcase","360","rotation"]'),
          ('product_lifestyle','Product Lifestyle','Product in real lifestyle context with natural use','product','medium','{product} being used naturally in everyday lifestyle scene, warm lighting, authentic moment',10,'static','subtle','["product","lifestyle","context","authentic"]'),
          ('product_unboxing','Product Unboxing','Unboxing sequence with reveal and first impressions','product','easy','{product} unboxing, hands opening packaging, reveal moment, first impression reaction',10,'static','medium','["product","unboxing","reveal","hands"]'),
          ('food_closeup','Food Close-up','Appetizing close-up with steam, texture, and color','food','easy','{food} close-up, steam rising, appetizing texture, vibrant colors, shallow depth of field',5,'static','subtle','["food","closeup","appetizing","steam"]'),
          ('food_cooking','Food Cooking','Cooking process with dynamic motion and ingredients','food','medium','{food} being cooked, sizzling, ingredients being added, steam and motion, dynamic cooking scene',8,'static','medium','["food","cooking","dynamic","sizzling"]'),
          ('food_plating','Food Plating','Artistic plating and garnishing process','food','medium','{food} being artistically plated, garnish being added, chef hands, premium presentation',10,'static','subtle','["food","plating","artistic","presentation"]'),
          ('nature_landscape','Nature Landscape','Wide landscape with clouds, water, and natural motion','nature','easy','{landscape} landscape, clouds moving, water flowing, natural peaceful motion, golden hour lighting',10,'pan','subtle','["nature","landscape","pan","clouds","water"]'),
          ('nature_timelapse','Nature Timelapse','Fast motion of natural phenomena like sunset or flowers','nature','medium','{nature_scene} timelapse, fast motion, sunset colors changing, flowers blooming, clouds racing',10,'static','dramatic','["nature","timelapse","fast","sunset"]'),
          ('nature_weather','Nature Weather','Dramatic weather effects like rain, snow, or storms','nature','hard','{weather_scene} dramatic weather, rain falling, snow drifting, storm clouds, atmospheric intensity',8,'static','dramatic','["nature","weather","rain","storm","dramatic"]'),
          ('urban_city','Urban City','Cityscape with traffic, people, and urban energy','urban','medium','{cityscape} city scene, traffic flowing, people walking, urban energy, evening lights',8,'pan','medium','["urban","city","traffic","people"]'),
          ('urban_architecture','Urban Architecture','Architectural details with dynamic camera movement','urban','medium','{architecture} building, architectural details, dynamic camera movement, dramatic angles, shadows',8,'orbit','medium','["urban","architecture","building","camera"]'),
          ('abstract_art','Abstract Art','Abstract artistic motion with colors and shapes','abstract','medium','{abstract_concept} abstract art, flowing colors, morphing shapes, artistic motion, creative expression',8,'static','medium','["abstract","art","colors","shapes","creative"]')
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.drop_table("lab_recipe_proposals")
    op.drop_table("lab_benchmarks")
    op.drop_table("lab_photos")
    op.drop_table("lab_scenarios")
