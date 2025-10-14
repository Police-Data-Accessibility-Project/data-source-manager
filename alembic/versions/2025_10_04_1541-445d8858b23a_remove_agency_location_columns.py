"""Remove agency location columns

Revision ID: 445d8858b23a
Revises: dc6ab5157c49
Create Date: 2025-10-04 15:41:52.384222

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '445d8858b23a'
down_revision: Union[str, None] = 'dc6ab5157c49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = 'agencies'

def upgrade() -> None:
    op.drop_column(TABLE_NAME, 'locality')
    op.drop_column(TABLE_NAME, 'state')
    op.drop_column(TABLE_NAME, 'county')


def downgrade() -> None:
    pass
