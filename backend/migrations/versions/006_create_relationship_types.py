"""Create relationship_types table

Revision ID: 006_create_relationship_types
Revises: 005_create_audit_logs
Create Date: 2026-08-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006_create_relationship_types"
down_revision: Union[str, None] = "005_create_audit_logs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "relationship_types",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
    )
    op.create_index("ix_relationship_types_code", "relationship_types", ["code"])

    op.execute("""
        INSERT INTO relationship_types (code, title, sort_order, is_active)
        VALUES
          ('parent','Родитель',0,true),
          ('child','Ребёнок',1,true),
          ('spouse','Супруг/супруга',2,true),
          ('partner','Партнёр',3,true),
          ('friend','Друг',4,true),
          ('colleague','Коллега',5,true),
          ('boss','Начальник',6,true),
          ('sibling','Брат/сестра',7,true),
          ('grandparent','Бабушка/дедушка',8,true),
          ('grandchild','Внук/внучка',9,true),
          ('classmate','Одноклассник',10,true),
          ('teacher','Учитель',11,true),
          ('relative','Родственник',12,true)
    """)


def downgrade() -> None:
    op.drop_index("ix_relationship_types_code", table_name="relationship_types")
    op.drop_table("relationship_types")
