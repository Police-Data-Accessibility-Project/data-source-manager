"""Add task cleanup task

Revision ID: c5c20af87511
Revises: 241fd3925f5d
Create Date: 2025-10-03 15:46:00.212674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5c20af87511'
down_revision: Union[str, None] = '241fd3925f5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    ALTER TYPE task_type ADD VALUE 'Task Cleanup'
    """)


def downgrade() -> None:
    pass
