"""Create feedback table

Revision ID: 012_create_feedback
Revises: 011_add_qa_checklist
Create Date: 2026-08-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "012_create_feedback"
down_revision: Union[str, None] = "011_add_qa_checklist"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "feedback",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("generation_id", sa.UUID(as_uuid=True)),
        sa.Column("reaction", sa.String(30), nullable=False),
        sa.Column("details", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_feedback_user", "feedback", ["user_id"])
    op.create_index("ix_feedback_generation", "feedback", ["generation_id"])


def downgrade() -> None:
    op.drop_index("ix_feedback_generation", table_name="feedback")
    op.drop_index("ix_feedback_user", table_name="feedback")
    op.drop_table("feedback")
