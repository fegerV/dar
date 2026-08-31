"""Add telegram_user_id to users table

Revision ID: 020_add_telegram_user_id
Revises: 019_add_deleted_archived_indexes
Create Date: 2026-08-19

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "020_add_telegram_user_id"
down_revision: str | None = "019_add_deleted_archived_indexes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("telegram_user_id", sa.BigInteger, nullable=True))
    op.create_index("ix_users_telegram_user_id", "users", ["telegram_user_id"])


def downgrade() -> None:
    op.drop_index("ix_users_telegram_user_id", table_name="users")
    op.drop_column("users", "telegram_user_id")
