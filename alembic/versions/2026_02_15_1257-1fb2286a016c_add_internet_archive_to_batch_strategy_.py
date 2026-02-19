"""add internet_archive to batch_strategy enum

Revision ID: 1fb2286a016c
Revises: 1d3398f9cd8a
Create Date: 2026-02-15 12:57:34.550327

"""
from typing import Sequence, Union

from alembic import op

from src.util.alembic_helpers import switch_enum_type

# revision identifiers, used by Alembic.
revision: str = '1fb2286a016c'
down_revision: Union[str, None] = '759ce7d0772b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    switch_enum_type(
        table_name="batches",
        column_name="strategy",
        enum_name="batch_strategy",
        new_enum_values=[
            "example",
            "ckan",
            "muckrock_county_search",
            "auto_googler",
            "muckrock_all_search",
            "muckrock_simple_search",
            "common_crawler",
            "manual",
            "internet_archive",
        ],
    )


def downgrade() -> None:
    op.execute("""
    DELETE FROM BATCHES
        WHERE STRATEGY = 'internet_archive'
    """)

    switch_enum_type(
        table_name="batches",
        column_name="strategy",
        enum_name="batch_strategy",
        new_enum_values=[
            "example",
            "ckan",
            "muckrock_county_search",
            "auto_googler",
            "muckrock_all_search",
            "muckrock_simple_search",
            "common_crawler",
            "manual",
        ],
    )
