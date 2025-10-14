"""Remove unused batches columns

Revision ID: f708c6a8ae5d
Revises: 445d8858b23a
Create Date: 2025-10-04 16:40:11.064794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f708c6a8ae5d'
down_revision: Union[str, None] = '445d8858b23a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "batches"

def upgrade() -> None:
    op.drop_column(TABLE_NAME, "strategy_success_rate")
    op.drop_column(TABLE_NAME, "metadata_success_rate")
    op.drop_column(TABLE_NAME, "agency_match_rate")
    op.drop_column(TABLE_NAME, "record_type_match_rate")
    op.drop_column(TABLE_NAME, "record_category_match_rate")


def downgrade() -> None:
    pass
