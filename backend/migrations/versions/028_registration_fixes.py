"""Add unique constraint on users.email, create email_verifications and webhook_endpoints tables

Revision ID: 028_registration_fixes
Revises: 027_create_refresh_tokens
Create Date: 2026-08-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "028_registration_fixes"
down_revision: Union[str, None] = "027_create_refresh_tokens"
branch_labels: Union[str, Sequence[str] | None] = None
depends_on: Union[str, Sequence[str] | None] = None


def upgrade() -> None:
    # Remove old non-unique index and create unique one on users.email
    op.drop_index("ix_users_email", table_name="users")
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # email_verifications table for email verification during registration
    op.create_table(
        "email_verifications",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_email_verifications_token", "email_verifications", ["token_hash"])
    op.create_index("ix_email_verifications_email", "email_verifications", ["email"])

    # webhook_endpoints table for user.registered event dispatch
    op.create_table(
        "webhook_endpoints",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("events", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("secret", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_webhook_endpoints_active", "webhook_endpoints", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_webhook_endpoints_active", table_name="webhook_endpoints")
    op.drop_table("webhook_endpoints")

    op.drop_index("ix_email_verifications_email", table_name="email_verifications")
    op.drop_index("ix_email_verifications_token", table_name="email_verifications")
    op.drop_table("email_verifications")

    # Restore original non-unique index
    op.drop_index("ix_users_email", table_name="users")
    op.create_index("ix_users_email", "users", ["email"], unique=False)
