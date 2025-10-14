"""Add new agency suggestion url link table

Revision ID: 50a710e413f8
Revises: d4c63e23d3f0
Create Date: 2025-09-26 20:02:10.867728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import url_id_column, agency_id_column, created_at_column

# revision identifiers, used by Alembic.
revision: str = '50a710e413f8'
down_revision: Union[str, None] = 'd4c63e23d3f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'link_url_new_agency_suggestion',
        url_id_column(),
        sa.Column(
            'suggestion_id',
            sa.Integer,
            sa.ForeignKey('new_agency_suggestions.id'), nullable=False
        ),
        created_at_column(),
        sa.PrimaryKeyConstraint(
            'url_id', 'suggestion_id'
        )
    )


def downgrade() -> None:
    pass
