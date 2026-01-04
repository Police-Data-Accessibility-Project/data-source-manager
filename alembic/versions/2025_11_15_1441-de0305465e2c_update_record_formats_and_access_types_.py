"""Update record_formats and access_types to be not null

Revision ID: de0305465e2c
Revises: a57c3b5b6e93
Create Date: 2025-11-15 14:41:45.619148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de0305465e2c'
down_revision: Union[str, None] = 'a57c3b5b6e93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLE_NAME = "url_optional_data_source_metadata"


def upgrade() -> None:
    _update_record_formats()
    _update_access_types()
    _alter_record_formats_column()
    _alter_access_types_column()

def _alter_record_formats_column():
    op.alter_column(
        table_name=TABLE_NAME,
        column_name="record_formats",
        nullable=False,
        server_default='{}'
    )


def _alter_access_types_column():
    op.alter_column(
        table_name=TABLE_NAME,
        column_name="access_types",
        nullable=False,
        server_default='{}'
    )



def _update_access_types():
    op.execute("""
    UPDATE url_optional_data_source_metadata
    SET access_types = '{}'
    WHERE access_types is null

    """)


def _update_record_formats():
    op.execute("""
    UPDATE url_optional_data_source_metadata
    SET record_formats = '{}'
    WHERE record_formats is null
    """)


def downgrade() -> None:
    pass
