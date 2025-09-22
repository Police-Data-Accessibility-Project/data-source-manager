"""Update suggestion constraints

Revision ID: 6b3db0c19f9b
Revises: 8d7208843b76
Create Date: 2025-09-22 13:09:42.830264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b3db0c19f9b'
down_revision: Union[str, None] = '8d7208843b76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        table_name="user_url_type_suggestions",
        constraint_name='uq_user_relevant_suggestions_url_id'
    )
    op.drop_constraint(
        table_name="user_url_agency_suggestions",
        constraint_name='uq_user_agency_suggestions_url_id'
    )
    op.drop_constraint(
        table_name="user_record_type_suggestions",
        constraint_name='uq_user_record_type_suggestions_url_id'
    )


def downgrade() -> None:
    op.create_unique_constraint(
        constraint_name='uq_user_relevant_suggestions_url_id',
        table_name="user_url_type_suggestions",
        columns=["url_id"],
    )
    op.create_unique_constraint(
        constraint_name='uq_user_agency_suggestions_url_id',
        table_name="user_url_agency_suggestions",
        columns=["url_id"],
    )
    op.create_unique_constraint(
        constraint_name='uq_user_record_type_suggestions_url_id',
        table_name="user_record_type_suggestions",
        columns=["url_id"],
    )
