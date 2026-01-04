"""Remove URL Status attribute

Revision ID: 759ce7d0772b
Revises: 42933d84aa52
Create Date: 2025-12-31 11:06:39.037486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '759ce7d0772b'
down_revision: Union[str, None] = '42933d84aa52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column(
        table_name="urls",
        column_name="status"
    )

    op.execute("""DROP type url_status""")


def downgrade() -> None:
    pass
