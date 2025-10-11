"""Add batch link subtasks

Revision ID: 8b2adc95c5d7
Revises: 7c4049508bfc
Create Date: 2025-10-11 14:38:01.874040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import add_enum_value

# revision identifiers, used by Alembic.
revision: str = '8b2adc95c5d7'
down_revision: Union[str, None] = '7c4049508bfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    add_enum_value(
        enum_name="agency_auto_suggestion_method",
        enum_value="batch_link"
    )
    add_enum_value(
        enum_name="auto_location_id_subtask_type",
        enum_value="batch_link"
    )


def downgrade() -> None:
    pass
