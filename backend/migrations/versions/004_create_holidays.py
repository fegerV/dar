"""Create holidays table

Revision ID: 004_create_holidays
Revises: 003_add_generation_eta
Create Date: 2026-08-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_create_holidays"
down_revision: Union[str, None] = "003_add_generation_eta"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "holidays",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("month", sa.Integer),
        sa.Column("day", sa.Integer),
        sa.Column("country_code", sa.String(2)),
        sa.Column("description", sa.Text),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_holidays_kind_status", "holidays", ["kind", "status"])
    op.create_index("ix_holidays_month_day", "holidays", ["month", "day"])

    op.execute("""
        INSERT INTO holidays (code, title, kind, month, day, country_code, description, status, metadata, created_at, updated_at)
        VALUES
          ('new_year', 'Новый год', 'state', 1, 1, 'RU', 'Государственный праздник', 'active', '{}', now(), now()),
          ('christmas', 'Рождество Христово', 'state', 1, 7, 'RU', 'Государственный праздник', 'active', '{}', now(), now()),
          ('feb23', '23 февраля', 'state', 2, 23, 'RU', 'День защитника Отечества', 'active', '{}', now(), now()),
          ('march8', '8 марта', 'state', 3, 8, 'RU', 'Международный женский день', 'active', '{}', now(), now()),
          ('may1', 'Праздник Весны и Труда', 'state', 5, 1, 'RU', 'Государственный праздник', 'active', '{}', now(), now()),
          ('victory_day', '9 мая', 'state', 5, 9, 'RU', 'День Победы', 'active', '{}', now(), now()),
          ('russia_day', 'День России', 'state', 6, 12, 'RU', 'Государственный праздник', 'active', '{}', now(), now()),
          ('unity_day', 'День народного единства', 'state', 11, 4, 'RU', 'Государственный праздник', 'active', '{}', now(), now()),
          ('programmer_day', 'День программиста', 'professional', 9, 13, 'RU', 'Профессиональный праздник', 'active', '{}', now(), now()),
          ('teacher_day', 'День учителя', 'professional', 10, 5, 'RU', 'Профессиональный праздник', 'active', '{}', now(), now()),
          ('builder_day', 'День строителя', 'professional', 8, 11, 'RU', 'Профессиональный праздник', 'active', '{}', now(), now()),
          ('doctor_day', 'День врача', 'professional', 6, 19, 'RU', 'Профессиональный праздник', 'active', '{}', now(), now()),
          ('valentines', 'День святого Валентина', 'thematic', 2, 14, 'RU', 'Праздник всех влюблённых', 'active', '{}', now(), now()),
          ('halloween', 'Хэллоуин', 'thematic', 10, 31, 'RU', 'Международный праздник', 'active', '{}', now(), now())
    """)


def downgrade() -> None:
    op.drop_index("ix_holidays_month_day", table_name="holidays")
    op.drop_index("ix_holidays_kind_status", table_name="holidays")
    op.drop_table("holidays")
