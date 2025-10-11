"""Add link tables for location_batch and agency_batch

Revision ID: 7c4049508bfc
Revises: dff1085d1c3d
Create Date: 2025-10-09 20:46:30.013715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import batch_id_column, location_id_column, created_at_column, agency_id_column

# revision identifiers, used by Alembic.
revision: str = '7c4049508bfc'
down_revision: Union[str, None] = 'dff1085d1c3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None





def upgrade() -> None:
    _create_link_location_batches_table()
    _create_link_agency_batches_table()

def _create_link_location_batches_table():
    op.create_table(
        "link_location_batches",
        batch_id_column(),
        location_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint(
            'batch_id',
            'location_id',
            name='link_location_batches_pk'
        )
    )


def _create_link_agency_batches_table():
    op.create_table(
        "link_agency_batches",
        batch_id_column(),
        agency_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint(
            'batch_id',
            'agency_id',
            name='link_agency_batches_pk'
        )
    )


def downgrade() -> None:
    pass
