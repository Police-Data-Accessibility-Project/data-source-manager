"""Add link__locations__user_follows table

Revision ID: e88e4e962dc7
Revises: 30ee666f15d1
Create Date: 2025-12-24 18:54:38.897466

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import add_enum_value, location_id_column, user_id_column, created_at_column

# revision identifiers, used by Alembic.
revision: str = 'e88e4e962dc7'
down_revision: Union[str, None] = '30ee666f15d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    _add_link_locations_user_follows_table()
    _add_follows_sync_task()

def _add_link_locations_user_follows_table():
    op.create_table(
        "link__locations__user_follows",
        location_id_column(),
        user_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint("location_id", "user_id"),
    )


def _add_follows_sync_task():
    add_enum_value(
        enum_name="task_type",
        enum_value="Sync User Follows Get"
    )

def downgrade() -> None:
    pass
