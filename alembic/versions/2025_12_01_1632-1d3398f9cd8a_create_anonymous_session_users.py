"""Create anonymous_session_users

Revision ID: 1d3398f9cd8a
Revises: 5d6412540aba
Create Date: 2025-12-01 16:32:27.842175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from src.util.alembic_helpers import created_at_column

# revision identifiers, used by Alembic.
revision: str = '1d3398f9cd8a'
down_revision: Union[str, None] = '5d6412540aba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def _alter_anonymous_annotation_agency():
    # Add new column
    op.add_column(
        "anonymous_annotation_agency",
        sa.Column(
            "session_id",
            UUID,
            sa.ForeignKey("anonymous_sessions.id"),
            nullable=False
        )
    )

    # Drop prior unique constraint/primary key
    op.drop_constraint(
        "anonymous_annotation_agency_pkey",
        "anonymous_annotation_agency"
    )

    # Add new unique constraint/primary key
    op.create_primary_key(
        "anonymous_annotation_agency_pkey",
        "anonymous_annotation_agency",
        ["session_id", "url_id", "agency_id"]
    )

def _alter_anonymous_annotation_location():
    # Add new column
    op.add_column(
        "anonymous_annotation_location",
        sa.Column(
            "session_id",
            UUID,
            sa.ForeignKey("anonymous_sessions.id"),
            nullable=False
        )
    )

    # Drop prior unique constraint/primary key
    op.drop_constraint(
        "anonymous_annotation_location_pkey",
        "anonymous_annotation_location"
    )

    # Add new unique constraint/primary key
    op.create_primary_key(
        "anonymous_annotation_location_pkey",
        "anonymous_annotation_location",
        ["session_id", "url_id", "location_id"]
    )

def _alter_anonymous_annotation_record_type():
    # Add new column
    op.add_column(
        "anonymous_annotation_record_type",
        sa.Column(
            "session_id",
            UUID,
            sa.ForeignKey("anonymous_sessions.id"),
            nullable=False
        )
    )

    # Drop prior unique constraint/primary key
    op.drop_constraint(
        "anonymous_annotation_record_type_pkey",
        "anonymous_annotation_record_type"
    )

    # Add new unique constraint/primary key
    op.create_primary_key(
        "anonymous_annotation_record_type_pkey",
        "anonymous_annotation_record_type",
        ["session_id", "url_id", "record_type"]
    )

def _alter_anonymous_annotation_url_type():
    # Add new column
    op.add_column(
        "anonymous_annotation_url_type",
        sa.Column(
            "session_id",
            UUID,
            sa.ForeignKey("anonymous_sessions.id"),
            nullable=False
        )
    )

    # Drop prior unique constraint/primary key
    op.drop_constraint(
        "anonymous_annotation_url_type_pkey",
        "anonymous_annotation_url_type"
    )

    # Add new unique constraint/primary key
    op.create_primary_key(
        "anonymous_annotation_url_type_pkey",
        "anonymous_annotation_url_type",
        ["session_id", "url_id", "url_type"]
    )

def upgrade() -> None:
    # Create anonymous_sessions table
    _create_anonymous_sessions_table()

    # Remove all prior anonymous annotations
    _remove_prior_sessions()

    _alter_anonymous_annotation_agency()
    _alter_anonymous_annotation_location()
    _alter_anonymous_annotation_record_type()
    _alter_anonymous_annotation_url_type()


def _remove_prior_sessions():
    for table in [
        "anonymous_annotation_agency",
        "anonymous_annotation_location",
        "anonymous_annotation_record_type",
        "anonymous_annotation_url_type"
    ]:
        op.execute(
            f"""
            DELETE FROM {table}
        """
            )


def _create_anonymous_sessions_table():
    op.create_table(
        "anonymous_sessions",
        sa.Column(
            "id",
            UUID,
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True
        ),
        created_at_column()
    )


def downgrade() -> None:
    pass
