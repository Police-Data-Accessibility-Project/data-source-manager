"""Add url_task_error table and remove url_error_info

Revision ID: dc6ab5157c49
Revises: c5c20af87511
Create Date: 2025-10-03 18:31:54.887740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

from src.util.alembic_helpers import url_id_column, task_id_column, created_at_column

# revision identifiers, used by Alembic.
revision: str = 'dc6ab5157c49'
down_revision: Union[str, None] = 'c5c20af87511'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None





def upgrade() -> None:
    _remove_url_error_info()
    _remove_url_screenshot_error()
    _add_url_task_error()

def _remove_url_error_info():
    op.drop_table("url_error_info")

def _remove_url_screenshot_error():
    op.drop_table("error_url_screenshot")

def _add_url_task_error():
    op.create_table(
        "url_task_error",
        url_id_column(),
        task_id_column(),
        sa.Column(
            "task_type",
            ENUM(name="task_type", create_type=False)
        ),
        sa.Column("error", sa.String(), nullable=False),
        created_at_column(),
        sa.PrimaryKeyConstraint("url_id", "task_type")
  )



def downgrade() -> None:
    pass
