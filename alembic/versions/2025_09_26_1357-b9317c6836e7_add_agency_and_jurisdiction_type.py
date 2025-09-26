"""Add agency and jurisdiction type

Revision ID: b9317c6836e7
Revises: 7b955c783e27
Create Date: 2025-09-26 13:57:42.357788

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9317c6836e7'
down_revision: Union[str, None] = '7b955c783e27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_agency_type_column():
    agency_type_enum = sa.Enum(
                "unknown",
                "incarceration",
                "law enforcement",
                "court",
                "aggregated",
                name="agency_type_enum",
                create_type=True,
            )
    agency_type_enum.create(op.get_bind())

    op.add_column(
        table_name="agencies",
        column=sa.Column(
            "agency_type",
            agency_type_enum,
            server_default="unknown",
            nullable=False,
        )
    )


def _add_jurisdiction_type_column():
    jurisdiction_type_enum = sa.Enum(
                'school', 'county', 'local', 'port', 'tribal', 'transit', 'state', 'federal',
                name="jurisdiction_type_enum",
            )
    jurisdiction_type_enum.create(op.get_bind())

    op.add_column(
        table_name="agencies",
        column=sa.Column(
            "jurisdiction_type",
            jurisdiction_type_enum,
            nullable=True,
        )
    )


def upgrade() -> None:
    _add_agency_type_column()
    _add_jurisdiction_type_column()


def downgrade() -> None:
    pass
