"""Eliminate Contact Info and Agency Meta Record Type

Revision ID: 43077d7e08c5
Revises: 51bde16e22f7
Create Date: 2025-10-12 20:36:17.965218

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import remove_enum_value

# revision identifiers, used by Alembic.
revision: str = '43077d7e08c5'
down_revision: Union[str, None] = '51bde16e22f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """DELETE FROM URL_RECORD_TYPE WHERE RECORD_TYPE = 'Contact Info & Agency Meta'"""
    )
    op.execute(
        """DELETE FROM auto_record_type_suggestions WHERE record_type = 'Contact Info & Agency Meta'"""
    )
    op.execute(
        """DELETE FROM user_record_type_suggestions WHERE record_type = 'Contact Info & Agency Meta'"""
    )

    remove_enum_value(
        enum_name="record_type",
        value_to_remove="Contact Info & Agency Meta",
        targets=[
            ("url_record_type", "record_type"),
            ("auto_record_type_suggestions", "record_type"),
            ("user_record_type_suggestions", "record_type")
        ]
    )


def downgrade() -> None:
    pass
