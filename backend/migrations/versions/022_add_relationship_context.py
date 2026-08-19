"""Add relationship subtypes, groups, and shared memories tables

Revision ID: 022_add_relationship_context
Revises: 021_add_promo_codes
Create Date: 2026-08-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "022_add_relationship_context"
down_revision: Union[str, None] = "021_add_promo_codes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table(
        "relationship_subtypes",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("parent_code", sa.String(50), nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("metadata", sa.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "recipient_groups",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("owner_user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("metadata", sa.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("owner_user_id", "code", name="uq_recipient_groups_owner_code"),
    )

    op.create_table(
        "recipient_shared_memories",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("recipient_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("group_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("tags", sa.JSONB, nullable=False, server_default="[]"),
        sa.Column("remind_before_days", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.execute("""
        INSERT INTO relationship_subtypes (code, title, parent_code, sort_order, is_active)
        VALUES
          ('parent_child','Родитель/Ребёнок','parent',0,true),
          ('parent_child','Родитель/Ребёнок','child',1,true),
          ('spouse_partner','Супруг/Партнёр','spouse',0,true),
          ('spouse_partner','Супруг/Партнёр','partner',1,true),
          ('family_extended','Родственник','relative',0,true),
          ('friend_close','Близкий друг','friend',0,true),
          ('friend_casual','Знакомый','friend',1,true),
          ('work_colleague','Коллега','colleague',0,true),
          ('work_boss','Начальник','boss',0,true),
          ('work_subordinate','Подчинённый','colleague',1,true)
    """)


def downgrade() -> None:
    op.drop_table("recipient_shared_memories")
    op.drop_table("recipient_groups")
    op.drop_table("relationship_subtypes")
