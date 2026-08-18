"""Add indexes for deleted_at and archived_at columns

Revision ID: 019_add_deleted_archived_indexes
Revises: 018_add_is_admin_to_users
Create Date: 2026-08-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "019_add_deleted_archived_indexes"
down_revision: Union[str, None] = "018_add_is_admin_to_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_index("ix_users_deleted_at", "users", ["deleted_at"])
    op.create_index("ix_recipients_archived_at", "recipients", ["archived_at"])


def downgrade() -> None:
    op.drop_index("ix_users_deleted_at", table_name="users")
    op.drop_index("ix_recipients_archived_at", "recipients")
