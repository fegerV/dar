"""Create referral tables

Revision ID: 009_create_referrals
Revises: 008_add_scene_condition
Create Date: 2026-08-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009_create_referrals"
down_revision: Union[str, None] = "008_add_scene_condition"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "referral_codes",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("uses_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("max_uses", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_referral_codes_code", "referral_codes", ["code"])
    op.create_index("ix_referral_codes_user", "referral_codes", ["user_id"])

    op.create_table(
        "referrals",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("referrer_user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("referred_user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("referrer_bonus_granted", sa.Boolean, nullable=False, server_default="false"),
         sa.Column("referee_bonus_granted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_referrals_referrer", "referrals", ["referrer_user_id"])
    op.create_index("ix_referrals_referred", "referrals", ["referred_user_id"])
    op.create_index("ix_referrals_code", "referrals", ["code"])


def downgrade() -> None:
    op.drop_index("ix_referrals_code", table_name="referrals")
    op.drop_index("ix_referrals_referred", table_name="referrals")
    op.drop_index("ix_referrals_referrer", table_name="referrals")
    op.drop_table("referrals")
    op.drop_index("ix_referral_codes_user", table_name="referral_codes")
    op.drop_index("ix_referral_codes_code", table_name="referral_codes")
    op.drop_table("referral_codes")
