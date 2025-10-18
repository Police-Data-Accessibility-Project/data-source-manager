"""Add trailing slash column

Revision ID: 7fc6502f1fa3
Revises: ff4e8b2f6348
Create Date: 2025-10-17 18:26:56.756915

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fc6502f1fa3'
down_revision: Union[str, None] = 'ff4e8b2f6348'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _remove_duplicates()
    _add_trailing_slash_column()
    _migrate_trailing_slash_to_column()
    _remove_trailing_slash_from_url_column()
    _add_check_constraint_forbidding_trailing_slash_in_url()

def _remove_duplicates():
    op.execute(
        """
        DELETE FROM urls
        WHERE id IN (
            23504,
            29401,
            21032,
            23687,
            15760,
            17574,
            17669,
            21382,
            11697,
            18076,
            27764,
            11395,
            17702,
            26857,
            30843,
            21850,
            29471,
            26789,
            19428,
            18452,
            30547,
            24004,
            27857,
            30260,
            26968,
            27065,
            29073,
            21827,
            25615,
            28644,
            24417,
            29801,
            27625,
            15708,
            23517,
            26415,
            26081,
            7478,
            20368,
            19494,
            26624,
            3817,
            3597,
            3568,
            16113,
            24125,
            30625,
            29965,
            23134,
            19207,
            12158,
            3835,
            24730,
            17113,
            29987,
            21452,
            24605,
            5043,
            17237,
            25522,
            11065,
            12387,
            12210,
            11185,
            11961,
            4935,
            24200,
            29028,
            24371,
            28355,
            17620,
            19546,
            3598
        )
        """
    )

def _add_trailing_slash_column():
    op.add_column(
        'urls',
        sa.Column(
            'trailing_slash',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false')
        )
    )

def _migrate_trailing_slash_to_column():
    op.execute(
        """
        UPDATE urls
        SET trailing_slash = url ~ '/$'
        """
    )

def _remove_trailing_slash_from_url_column():
    op.execute(
        """
        UPDATE urls
        SET url = rtrim(url, '/')
        WHERE url like '%/';
        """
    )

def _add_check_constraint_forbidding_trailing_slash_in_url():
    op.execute(
        """
        ALTER TABLE urls
        ADD CONSTRAINT no_trailing_slash CHECK (url !~ '/$')
        """
    )

def downgrade() -> None:
    pass
