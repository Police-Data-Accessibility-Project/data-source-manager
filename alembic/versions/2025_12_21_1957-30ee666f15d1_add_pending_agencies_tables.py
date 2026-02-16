"""Add pending agencies tables

Revision ID: 30ee666f15d1
Revises: 9292faed37fd
Create Date: 2025-12-21 19:57:58.199838

Design notes:

After debating it internally, I elected to have a separate pending agencies table,
rather than adding an `approval status` column to the agencies table.

This is for a few reasons:
 1. Many existing queries and models rely on the current agency setup,
    and would need to be retrofitted in order to filter
    approved and unapproved agencies.
 2. Some existing links, such as between agencies and batches, between agencies and URLs,
    or agency annotations for URLs, would not make sense for pending agencies,
    and would be difficult to prevent in the database.

This setup does, however, make it more difficult to check for duplicates between
existing agencies and pending agencies. However, I concluded it was better for
pending agencies to be negatively affected by these design choices than
for existing agencies to be affected by the above design choices.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import id_column, created_at_column, enum_column, agency_id_column

# revision identifiers, used by Alembic.
revision: str = '30ee666f15d1'
down_revision: Union[str, None] = '9292faed37fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade() -> None:
    _create_proposed_agency_table()
    _create_proposed_agency_location_table()
    _create_proposed_agency_decision_info_table()

def _create_proposed_agency_decision_info_table():
    op.create_table(
        "proposal__agencies__decision_info",
        sa.Column("proposal_agency_id", sa.Integer(), sa.ForeignKey("proposal__agencies.id"), nullable=False),
        sa.Column("deciding_user_id", sa.Integer),
        sa.Column("rejection_reason", sa.String(), nullable=True),
        created_at_column(),
        sa.PrimaryKeyConstraint("proposal_agency_id")
    )


def _create_proposed_agency_table():
    op.execute("CREATE TYPE proposal_status_enum AS ENUM ('pending', 'approved', 'rejected');")

    op.create_table(
        "proposal__agencies",
        id_column(),
        sa.Column("name", sa.String(), nullable=False),
        enum_column(
            column_name="agency_type",
            enum_name="agency_type_enum",
        ),
        enum_column(
            column_name="jurisdiction_type",
            enum_name="jurisdiction_type_enum"
        ),
        sa.Column("proposing_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "promoted_agency_id",
            sa.Integer(),
            sa.ForeignKey(
                "agencies.id"
            )
        ),
        enum_column(
            column_name="proposal_status",
            enum_name="proposal_status_enum",
        ),
        created_at_column(),
        sa.CheckConstraint(
            "promoted_agency_id IS NULL OR proposal_status = 'pending'",
            name="ck_agency_id_or_proposal_status"
        )
    )

def _create_proposed_agency_location_table():
    op.create_table(
        "proposal__link__agencies__locations",
        sa.Column(
            "proposal_agency_id",
            sa.Integer(),
            sa.ForeignKey("proposal__agencies.id"),
            nullable=False,
        ),
        sa.Column(
            "location_id",
            sa.Integer(),
            sa.ForeignKey("locations.id"),
            nullable=False
        ),
        created_at_column(),
        sa.PrimaryKeyConstraint("proposal_agency_id", "location_id")
    )

def downgrade() -> None:
    pass
