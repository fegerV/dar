"""Add is_admin to users table

Revision ID: 018_add_is_admin_to_users
Revises: 017_create_admin_tables
Create Date: 2026-08-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "018_add_is_admin_to_users"
down_revision: Union[str, None] = "017_create_admin_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_admin", sa.Boolean, nullable=False, server_default=sa.text("false")))


def downgrade() -> None:
    op.drop_column("users", "is_admin")
