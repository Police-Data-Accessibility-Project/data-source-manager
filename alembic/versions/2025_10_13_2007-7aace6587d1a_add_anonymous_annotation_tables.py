"""Add anonymous annotation tables

Revision ID: 7aace6587d1a
Revises: 43077d7e08c5
Create Date: 2025-10-13 20:07:18.388899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import url_id_column, agency_id_column, created_at_column, location_id_column, enum_column

# revision identifiers, used by Alembic.
revision: str = '7aace6587d1a'
down_revision: Union[str, None] = '43077d7e08c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "anonymous_annotation_agency",
        url_id_column(),
        agency_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint('url_id', 'agency_id')
    )
    op.create_table(
        "anonymous_annotation_location",
        url_id_column(),
        location_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint('url_id', 'location_id')
    )
    op.create_table(
        "anonymous_annotation_record_type",
        url_id_column(),
        enum_column(
            column_name="record_type",
            enum_name="record_type"
        ),
        created_at_column(),
        sa.PrimaryKeyConstraint('url_id', 'record_type')
    )
    op.create_table(
        "anonymous_annotation_url_type",
        url_id_column(),
        enum_column(
            column_name="url_type",
            enum_name="url_type"
        ),
        created_at_column(),
        sa.PrimaryKeyConstraint('url_id', 'url_type')
    )


def downgrade() -> None:
    pass
