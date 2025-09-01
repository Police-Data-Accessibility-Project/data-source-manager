"""Augment auto_agency_suggestions

Revision ID: b741b65a1431
Revises: 8a70ee509a74
Create Date: 2025-08-19 08:03:12.106575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import created_at_column, updated_at_column, id_column, url_id_column, switch_enum_type

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
    name="agency_auto_suggestion_method",
)

FLAG_URL_VALIDATED_TABLE_NAME = "flag_url_validated"

VALIDATED_URL_TYPE_ENUM = sa.Enum(
    "data source",
    "meta url",
    "not relevant",
    "individual record",
    name="validated_url_type"
)




def upgrade() -> None:
    op.rename_table(OLD_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME, NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME)
    op.rename_table(OLD_LINK_URLS_AGENCY_TABLE_NAME, NEW_LINK_URLS_AGENCY_TABLE_NAME)
    _alter_auto_agency_suggestions_table()
    _create_flag_url_validated_table()
    _add_urls_to_flag_url_validated_table()
    _remove_validated_and_submitted_url_statuses()
    _reset_agencies_sync_state()


def downgrade() -> None:
    op.rename_table(NEW_LINK_URLS_AGENCY_TABLE_NAME, OLD_LINK_URLS_AGENCY_TABLE_NAME)
    _revert_auto_agency_suggestions_table()
    op.rename_table(NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME, OLD_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME)
    _revert_url_statuses()
    _update_validated_and_submitted_url_statuses()
    op.drop_table(FLAG_URL_VALIDATED_TABLE_NAME)
    _drop_validated_url_type_enum()

def _reset_agencies_sync_state():
    op.execute(
        """
        UPDATE agencies_sync_state
        set
            last_full_sync_at = null,
            current_cutoff_date = null,
            current_page = null
        """
    )

def _remove_validated_and_submitted_url_statuses():
    switch_enum_type(
        table_name="urls",
        column_name="status",
        enum_name="url_status",
        new_enum_values=[
            'ok',
            'duplicate',
            'error',
            '404 not found',
        ],
        check_constraints_to_drop=['url_name_not_null_when_validated'],
        conversion_mappings={
            'validated': 'ok',
            'submitted': 'ok',
            'pending': 'ok',
            'not relevant': 'ok',
            'individual record': 'ok'
        }
    )

def _add_urls_to_flag_url_validated_table():
    op.execute("""
    INSERT INTO flag_url_validated (url_id, type)
    SELECT 
        urls.id, 
           CASE urls.status::text
               WHEN 'validated' THEN 'data source'
               WHEN 'submitted' THEN 'data source'
               ELSE urls.status::text
           END::validated_url_type
    FROM urls
    WHERE urls.status in ('validated', 'submitted', 'individual record', 'not relevant')""")

def _revert_url_statuses():
    switch_enum_type(
        table_name="urls",
        column_name="status",
        enum_name="url_status",
        new_enum_values=[
            'pending',
            'validated',
            'submitted',
            'duplicate',
            'not relevant',
            'error',
            '404 not found',
            'individual record'
        ],
        conversion_mappings={
            'ok': 'pending',
        }
    )
    op.create_check_constraint(
        "url_name_not_null_when_validated",
        "urls",
        "(name IS NOT NULL) OR (status <> 'validated'::url_status)"
    )

def _update_validated_and_submitted_url_statuses():
    op.execute("""
    UPDATE urls
    SET status = 'not relevant'
    FROM flag_url_validated
    WHERE urls.id = flag_url_validated.id
    AND flag_url_validated.type = 'not relevant'
    """)

    op.execute("""
    UPDATE urls
    SET status = 'individual record'
    FROM flag_url_validated
    WHERE urls.id = flag_url_validated.id
    AND flag_url_validated.type = 'individual record'
    """)

    op.execute("""
    UPDATE urls
    SET status = 'validated'
    FROM flag_url_validated
    left join url_data_source on flag_url_validated.url_id = url_data_source.url_id
    WHERE urls.id = flag_url_validated.id
    AND flag_url_validated.type = 'data source'
    AND url_data_source.url_id is NULL
    """)

    op.execute("""
    UPDATE urls
    SET status = 'validated'
    FROM flag_url_validated
    left join url_data_source on flag_url_validated.url_id = url_data_source.url_id
    WHERE urls.id = flag_url_validated.id
    AND flag_url_validated.type = 'data source'
    AND url_data_source.url_id is not NULL
    """)


def _create_flag_url_validated_table():
    op.create_table(
        FLAG_URL_VALIDATED_TABLE_NAME,
        id_column(),
        url_id_column(),
        sa.Column(
            'type',
            VALIDATED_URL_TYPE_ENUM,
            nullable=False,
        ),
        created_at_column(),
        updated_at_column(),
        sa.UniqueConstraint('url_id', name='uq_flag_url_validated_url_id')
    )

def _drop_validated_url_type_enum():
    VALIDATED_URL_TYPE_ENUM.drop(op.get_bind())

def _alter_auto_agency_suggestions_table():
    AGENCY_AUTO_SUGGESTION_METHOD_ENUM.create(op.get_bind())
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
        sa.Column(
            'method',
            AGENCY_AUTO_SUGGESTION_METHOD_ENUM,
            nullable=True
        )
    )
    # Confidence
    op.add_column(
        NEW_AUTO_URL_AGENCY_SUGGESTIONS_TABLE_NAME,
        sa.Column(
            'confidence',
            sa.Float(),
            server_default=sa.text('0.0'),
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
    AGENCY_AUTO_SUGGESTION_METHOD_ENUM.drop(op.get_bind())

