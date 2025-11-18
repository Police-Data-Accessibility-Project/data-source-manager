"""Add update_url_status task

Revision ID: 783268bd3daa
Revises: 88ac26c3b025
Create Date: 2025-11-18 09:02:54.985705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import add_enum_value

# revision identifiers, used by Alembic.
revision: str = '783268bd3daa'
down_revision: Union[str, None] = '88ac26c3b025'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    add_enum_value(
        enum_name="url_status",
        enum_value="broken"
    )
    add_enum_value(
        enum_name="task_type",
        enum_value="Update URL Status"
    )


def downgrade() -> None:
    pass
