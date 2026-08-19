"""Create viewing_reactions table

Revision ID: 023_add_viewing_reactions
Revises: 022_add_relationship_context
Create Date: 2026-08-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "023_add_viewing_reactions"
down_revision: Union[str, None] = "022_add_relationship_context"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table(
        "viewing_reactions",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("emoji", sa.String(10), nullable=False),
        sa.Column("rating", sa.Integer, nullable=True),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("negative_details_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_viewing_reactions_project_id", "viewing_reactions", ["project_id"])
    op.create_index("ix_viewing_reactions_user_id", "viewing_reactions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_viewing_reactions_user_id", table_name="viewing_reactions")
    op.drop_index("ix_viewing_reactions_project_id", table_name="viewing_reactions")
    op.drop_table("viewing_reactions")
