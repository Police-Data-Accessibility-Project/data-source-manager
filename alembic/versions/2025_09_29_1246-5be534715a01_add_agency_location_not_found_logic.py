"""Add Agency/Location Not Found Logic

Revision ID: 5be534715a01
Revises: 50a710e413f8
Create Date: 2025-09-29 12:46:27.140173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import created_at_column, url_id_column, user_id_column

# revision identifiers, used by Alembic.
revision: str = '5be534715a01'
down_revision: Union[str, None] = '50a710e413f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    add_link_user_suggestion_agency_not_found_table()
    add_link_user_suggestion_location_not_found_table()
    add_flag_url_suspended_table()
    add_url_suspend_task_type()
    remove_link_url_new_agency_suggestion_table()
    remove_new_agency_suggestions_table()

def add_url_suspend_task_type():
    op.execute(
        """
        ALTER TYPE task_type ADD VALUE 'Suspend URLs';
        """
    )

def add_link_user_suggestion_agency_not_found_table():
    op.create_table(
        "link_user_suggestion_agency_not_found",
        user_id_column(),
        url_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint("user_id", "url_id"),
    )


def add_link_user_suggestion_location_not_found_table():
    op.create_table(
        "link_user_suggestion_location_not_found",
        user_id_column(),
        url_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint("user_id", "url_id"),
    )


def add_flag_url_suspended_table():
    op.create_table(
        "flag_url_suspended",
        url_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint("url_id"),
    )


def remove_link_url_new_agency_suggestion_table():
    op.drop_table("link_url_new_agency_suggestion")


def remove_new_agency_suggestions_table():
    op.drop_table("new_agency_suggestions")


def downgrade() -> None:
    pass
