"""Eliminate hanging data sources

Revision ID: 1bb2dfad3275
Revises: c4edeb795134
Create Date: 2025-11-23 18:50:55.557428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1bb2dfad3275'
down_revision: Union[str, None] = 'c4edeb795134'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    DELETE FROM ds_app_link_data_source ds
        USING ds_app_link_meta_url mu,
              flag_url_validated fuv
        WHERE ds.url_id = mu.url_id
          AND ds.url_id = fuv.url_id;
    """)


def downgrade() -> None:
    pass
