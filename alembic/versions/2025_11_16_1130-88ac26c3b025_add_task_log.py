"""Add task log 

Revision ID: 88ac26c3b025
Revises: de0305465e2c
Create Date: 2025-11-16 11:30:25.742630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import task_id_column, created_at_column

# revision identifiers, used by Alembic.
revision: str = '88ac26c3b025'
down_revision: Union[str, None] = 'de0305465e2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tasks__log",
        task_id_column(),
        sa.Column(
            "log",
            sa.Text,
            nullable=False,
        ),
        created_at_column(),
        sa.PrimaryKeyConstraint("task_id"),
    )


def downgrade() -> None:
    pass
