"""Create ledger_transactions table

Revision ID: 030_create_ledger_transactions
Revises: 029_brief_autosave
Create Date: 2026-08-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "030_create_ledger_transactions"
down_revision: Union[str, None] = "029_brief_autosave"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ledger_transactions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("wallet_id", sa.UUID(as_uuid=True), sa.ForeignKey("wallets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("type", sa.String(30), nullable=False),
        sa.Column("amount_rub", sa.Numeric(14, 2), nullable=False),
        sa.Column("is_bonus", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("admin_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("reference_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ledger_transactions")
