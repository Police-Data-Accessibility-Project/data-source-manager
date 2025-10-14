"""Add URL record type

Revision ID: e6a1a1b3bad4
Revises: 6b3db0c19f9b
Create Date: 2025-09-22 19:16:01.744304

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from src.util.alembic_helpers import url_id_column, created_at_column, id_column

# revision identifiers, used by Alembic.
revision: str = 'e6a1a1b3bad4'
down_revision: Union[str, None] = '6b3db0c19f9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

URL_RECORD_TYPE_TABLE_NAME = "url_record_type"




def upgrade() -> None:
    _create_url_record_type_table()
    _migrate_url_record_types_to_url_record_type_table()
    _drop_record_type_column()
    _drop_agencies_sync_state()
    _drop_data_sources_sync_state()

def _drop_agencies_sync_state():
    op.drop_table("agencies_sync_state")


def _drop_data_sources_sync_state():
    op.drop_table("data_sources_sync_state")


def _create_data_sources_sync_state():
    table = op.create_table(
        "data_sources_sync_state",
        id_column(),
        sa.Column('last_full_sync_at', sa.DateTime(), nullable=True),
        sa.Column('current_cutoff_date', sa.Date(), nullable=True),
        sa.Column('current_page', sa.Integer(), nullable=True),
    )
    # Add row to `data_sources_sync_state` table
    op.bulk_insert(
        table,
        [
            {
                "last_full_sync_at": None,
                "current_cutoff_date": None,
                "current_page": None
            }
        ]
    )


def _create_agencies_sync_state():
    table = op.create_table(
        'agencies_sync_state',
        id_column(),
        sa.Column('last_full_sync_at', sa.DateTime(), nullable=True),
        sa.Column('current_cutoff_date', sa.Date(), nullable=True),
        sa.Column('current_page', sa.Integer(), nullable=True),
    )

    # Add row to `agencies_sync_state` table
    op.bulk_insert(
        table,
        [
            {
                "last_full_sync_at": None,
                "current_cutoff_date": None,
                "current_page": None
            }
        ]
    )


def downgrade() -> None:
    _add_record_type_column()
    _migrate_url_record_types_from_url_record_type_table()
    _drop_url_record_type_table()
    _create_agencies_sync_state()
    _create_data_sources_sync_state()

def _drop_record_type_column():
    op.drop_column("urls", "record_type")

def _add_record_type_column():
    op.add_column("urls", sa.Column("record_type", postgresql.ENUM(name="record_type", create_type=False), nullable=True))


def _create_url_record_type_table():
    op.create_table(
        URL_RECORD_TYPE_TABLE_NAME,
        url_id_column(primary_key=True),
        sa.Column("record_type", postgresql.ENUM(name="record_type", create_type=False), nullable=False),
        created_at_column()
    )


def _drop_url_record_type_table():
    op.drop_table(URL_RECORD_TYPE_TABLE_NAME)


def _migrate_url_record_types_from_url_record_type_table():
    op.execute("""
    UPDATE urls
    SET record_type = url_record_type.record_type
    FROM url_record_type
    WHERE urls.id = url_record_type.url_id
    """)


def _migrate_url_record_types_to_url_record_type_table():
    op.execute("""
    INSERT INTO url_record_type (url_id, record_type)
    SELECT id, record_type
    FROM urls
    WHERE record_type IS NOT NULL
    """)
