"""Create admin tables: roles, user_roles, admin_users, workers, queue_jobs, system_settings

Revision ID: 017_create_admin_tables
Revises: 016_create_intelligence_tables
Create Date: 2026-08-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "017_create_admin_tables"
down_revision: Union[str, None] = "016_create_intelligence_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("permissions", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_roles_code", "roles", ["code"], unique=True)

    op.create_table(
        "user_roles",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("granted_by", sa.UUID(as_uuid=True)),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_roles_user", "user_roles", ["user_id"])
    op.create_index("ix_user_roles_role", "user_roles", ["role_id"])

    op.create_table(
        "admin_users",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="admin"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_admin_users_user_id", "admin_users", ["user_id"], unique=True)

    op.create_table(
        "workers",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(120), unique=True, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="idle"),
        sa.Column("gpu_model", sa.String(50)),
        sa.Column("gpu_vram_total_gb", sa.Integer),
        sa.Column("gpu_vram_used_gb", sa.Integer),
        sa.Column("cpu_usage_percent", sa.Float),
        sa.Column("jobs_today", sa.Integer, nullable=False, server_default="0"),
        sa.Column("failures_today", sa.Integer, nullable=False, server_default="0"),
        sa.Column("avg_generation_time_sec", sa.Float),
        sa.Column("last_heartbeat_at", sa.DateTime(timezone=True)),
        sa.Column("metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_workers_name", "workers", ["name"], unique=True)

    op.create_table(
        "queue_jobs",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("generation_id", sa.UUID(as_uuid=True), sa.ForeignKey("generations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("worker_id", sa.UUID(as_uuid=True), sa.ForeignKey("workers.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("priority", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_code", sa.String(50)),
        sa.Column("error_message", sa.Text),
        sa.Column("retry_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_queue_jobs_generation", "queue_jobs", ["generation_id"])
    op.create_index("ix_queue_jobs_worker", "queue_jobs", ["worker_id"])
    op.create_index("ix_queue_jobs_status", "queue_jobs", ["status"])

    op.create_table(
        "system_settings",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(120), unique=True, nullable=False),
        sa.Column("value", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("description", sa.Text),
        sa.Column("is_public", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_system_settings_key", "system_settings", ["key"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_system_settings_key", table_name="system_settings")
    op.drop_table("system_settings")
    op.drop_index("ix_queue_jobs_status", table_name="queue_jobs")
    op.drop_index("ix_queue_jobs_worker", table_name="queue_jobs")
    op.drop_index("ix_queue_jobs_generation", table_name="queue_jobs")
    op.drop_table("queue_jobs")
    op.drop_index("ix_workers_name", table_name="workers")
    op.drop_table("workers")
    op.drop_index("ix_admin_users_user_id", table_name="admin_users")
    op.drop_table("admin_users")
    op.drop_index("ix_user_roles_role", table_name="user_roles")
    op.drop_index("ix_user_roles_user", table_name="user_roles")
    op.drop_table("user_roles")
    op.drop_index("ix_roles_code", table_name="roles")
    op.drop_table("roles")
