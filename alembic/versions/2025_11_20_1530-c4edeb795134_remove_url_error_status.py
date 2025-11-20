"""Remove URL Error Status

Revision ID: c4edeb795134
Revises: b8a68f4260a4
Create Date: 2025-11-20 15:30:15.783191

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import remove_enum_value

# revision identifiers, used by Alembic.
revision: str = 'c4edeb795134'
down_revision: Union[str, None] = 'b8a68f4260a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    remove_enum_value(
        enum_name="url_status",
        value_to_remove="error",
        targets=[
            ("urls", "status")
        ]
    )


def downgrade() -> None:
    pass
