"""Augment auto_agency_suggestions

Revision ID: b741b65a1431
Revises: 8a70ee509a74
Create Date: 2025-08-19 08:03:12.106575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import created_at_column, updated_at_column

# revision identifiers, used by Alembic.
revision: str = 'b741b65a1431'
down_revision: Union[str, None] = '8a70ee509a74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME = "automated_url_agency_suggestions"
NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME = "url_auto_agency_suggestions"

OLD_LINK_URLS_AGENCY_TABLE_NAME = "link_urls_agencies"
NEW_LINK_URLS_AGENCY_TABLE_NAME = "link_urls_agency"

AGENCY_AUTO_SUGGESTION_METHOD_ENUM = sa.Enum(
    "homepage_match",
    "nlp_location_match",
    "muckrock_match",
    "ckan_match",
    "unknown",
    name="agency_auto_suggestion_method"
)

def upgrade() -> None:
    op.rename_table(OLD_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME, NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME)
    op.rename_table(OLD_LINK_URLS_AGENCY_TABLE_NAME, NEW_LINK_URLS_AGENCY_TABLE_NAME)
    _alter_auto_agency_suggestions_table()

def _alter_auto_agency_suggestions_table():
    # Created At
    op.add_column(
        NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME,
        created_at_column()
    )
    # Updated At
    op.add_column(
        NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME,
        updated_at_column()
    )
    # Method
    op.add_column(
        NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME,
        sa.Column('method', AGENCY_AUTO_SUGGESTION_METHOD_ENUM, default="unknown", nullable=False)
    )
    # Confidence
    op.add_column(
        NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME,
        sa.Column(
            'confidence',
            sa.Float(),
            default=0.0,
            nullable=False
        )
    )
    # Check constraint that confidence is between 0 and 1
    op.create_check_constraint(
        "auto_url_agency_suggestions_check_confidence_between_0_and_1",
        NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME,
        "confidence BETWEEN 0 AND 1"
    )


def _revert_auto_agency_suggestions_table():
    # Created At
    op.drop_column(
        NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME,
        'created_at'
    )
    # Updated At
    op.drop_column(
        NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME,
        'updated_at'
    )
    # Method
    op.drop_column(
        NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME,
        'method'
    )
    # Confidence
    op.drop_column(
        NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME,
        'confidence'
    )

def downgrade() -> None:
    op.rename_table(NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME, OLD_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME)
    op.rename_table(NEW_LINK_URLS_AGENCY_TABLE_NAME, OLD_LINK_URLS_AGENCY_TABLE_NAME)
    _revert_auto_agency_suggestions_table()
