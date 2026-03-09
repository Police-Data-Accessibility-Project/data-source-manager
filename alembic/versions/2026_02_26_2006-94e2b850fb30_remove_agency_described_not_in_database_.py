"""remove agency_described_not_in_database from url optional metadata

Revision ID: 94e2b850fb30
Revises: 1fb2286a016c
Create Date: 2026-02-26 20:06:49.423584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94e2b850fb30'
down_revision: Union[str, None] = '1fb2286a016c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column(
        'url_optional_data_source_metadata',
        'agency_described_not_in_database',
    )


def downgrade() -> None:
    op.add_column(
        'url_optional_data_source_metadata',
        sa.Column('agency_described_not_in_database', sa.Text(), nullable=True),
    )
