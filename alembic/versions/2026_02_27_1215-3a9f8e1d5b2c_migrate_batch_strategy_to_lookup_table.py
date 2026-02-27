"""Migrate batch strategy enum to lookup table

Revision ID: 3a9f8e1d5b2c
Revises: 1fb2286a016c
Create Date: 2026-02-27 12:15:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3a9f8e1d5b2c'
down_revision: Union[str, None] = '1fb2286a016c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

STRATEGY_VALUES = [
    "example",
    "ckan",
    "muckrock_county_search",
    "auto_googler",
    "muckrock_all_search",
    "muckrock_simple_search",
    "common_crawler",
    "manual",
    "internet_archive",
]


def upgrade() -> None:
    op.create_table(
        "batch_strategies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    values_sql = ", ".join(f"('{value}')" for value in STRATEGY_VALUES)
    op.execute(f"INSERT INTO batch_strategies (name) VALUES {values_sql}")

    op.add_column(
        "batches",
        sa.Column("batch_strategy_id", sa.Integer(), nullable=True),
    )
    op.execute("""
    UPDATE batches AS b
    SET batch_strategy_id = bs.id
    FROM batch_strategies AS bs
    WHERE b.strategy::text = bs.name
    """)
    op.alter_column("batches", "batch_strategy_id", nullable=False)
    op.create_foreign_key(
        "fk_batches_batch_strategy_id",
        "batches",
        "batch_strategies",
        ["batch_strategy_id"],
        ["id"],
    )
    op.create_index(
        "ix_batches_batch_strategy_id",
        "batches",
        ["batch_strategy_id"],
        unique=False,
    )

    op.drop_column("batches", "strategy")
    op.execute("DROP TYPE IF EXISTS batch_strategy")


def downgrade() -> None:
    batch_strategy_enum = postgresql.ENUM(
        *STRATEGY_VALUES,
        name="batch_strategy",
    )
    batch_strategy_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "batches",
        sa.Column("strategy", batch_strategy_enum, nullable=True),
    )
    op.execute("""
    UPDATE batches AS b
    SET strategy = bs.name::batch_strategy
    FROM batch_strategies AS bs
    WHERE b.batch_strategy_id = bs.id
    """)
    op.alter_column("batches", "strategy", nullable=False)

    op.drop_index("ix_batches_batch_strategy_id", table_name="batches")
    op.drop_constraint("fk_batches_batch_strategy_id", "batches", type_="foreignkey")
    op.drop_column("batches", "batch_strategy_id")
    op.drop_table("batch_strategies")
