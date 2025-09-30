"""Add link user submitted URL table

Revision ID: 84a3de626ad8
Revises: 5be534715a01
Create Date: 2025-09-30 10:46:16.552174

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import url_id_column, user_id_column, created_at_column

# revision identifiers, used by Alembic.
revision: str = '84a3de626ad8'
down_revision: Union[str, None] = '5be534715a01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "link_user_submitted_urls",
        url_id_column(),
        user_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint("url_id", "user_id"),
        sa.UniqueConstraint("url_id")
    )


def downgrade() -> None:
    pass
