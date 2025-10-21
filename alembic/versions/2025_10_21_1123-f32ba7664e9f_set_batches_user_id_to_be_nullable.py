"""Set batches.user_id to be nullable

Revision ID: f32ba7664e9f
Revises: 6adf9d894180
Create Date: 2025-10-21 11:23:35.611484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f32ba7664e9f'
down_revision: Union[str, None] = '6adf9d894180'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name='batches',
        column_name='user_id',
        nullable=True
    )


def downgrade() -> None:
    pass
