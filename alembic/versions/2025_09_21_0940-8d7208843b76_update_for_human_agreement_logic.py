"""Update for human agreement logic

Revision ID: 8d7208843b76
Revises: 93cbaa3b8e9b
Create Date: 2025-09-21 09:40:36.506827

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import switch_enum_type, url_id_column, created_at_column

# revision identifiers, used by Alembic.
revision: str = '8d7208843b76'
down_revision: Union[str, None] = '93cbaa3b8e9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

AUTO_VALIDATION_TASK_TYPE: str = 'Auto Validate'
URL_TYPE_NAME: str = 'url_type'
VALIDATED_URL_TYPE_NAME: str = 'validated_url_type'
FLAG_URL_VALIDATED_TABLE_NAME: str = 'flag_url_validated'

USER_RELEVANT_SUGGESTIONS_TABLE_NAME: str = 'user_relevant_suggestions'
USER_URL_TYPE_SUGGESTIONS_TABLE_NAME: str = 'user_url_type_suggestions'

FLAG_URL_AUTO_VALIDATED_TABLE_NAME: str = 'flag_url_auto_validated'


def _create_anno_count_view():
    op.execute("""
    CREATE OR REPLACE VIEW url_annotation_count_view AS
    with auto_location_count as (
    select
        u.id,
        count(anno.url_id) as cnt
    from urls u
    inner join public.auto_location_id_subtasks anno on u.id = anno.url_id
    group by u.id
)
, auto_agency_count as (
        select
        u.id,
        count(anno.url_id) as cnt
    from urls u
    inner join public.url_auto_agency_id_subtasks anno on u.id = anno.url_id
    group by u.id
)
, auto_url_type_count as (
        select
            u.id,
            count(anno.url_id) as cnt
        from urls u
             inner join public.auto_relevant_suggestions anno on u.id = anno.url_id
        group by u.id
)
, auto_record_type_count as (
        select
            u.id,
            count(anno.url_id) as cnt
        from urls u
             inner join public.auto_record_type_suggestions anno on u.id = anno.url_id
        group by u.id
)
, user_location_count as (
        select
            u.id,
            count(anno.url_id) as cnt
        from urls u
             inner join public.user_location_suggestions anno on u.id = anno.url_id
        group by u.id
)
, user_agency_count as (
        select
            u.id,
            count(anno.url_id) as cnt
        from urls u
             inner join public.user_url_agency_suggestions anno on u.id = anno.url_id
        group by u.id
)
, user_url_type_count as (
        select
            u.id,
            count(anno.url_id) as cnt
        from urls u
             inner join public.user_url_type_suggestions anno on u.id = anno.url_id
        group by u.id
        )
, user_record_type_count as (
        select
            u.id,
            count(anno.url_id) as cnt
        from urls u
             inner join public.user_record_type_suggestions anno on u.id = anno.url_id
        group by u.id
)
select
    u.id as url_id,
    coalesce(auto_ag.cnt, 0) as auto_agency_count,
    coalesce(auto_loc.cnt, 0) as auto_location_count,
    coalesce(auto_rec.cnt, 0) as auto_record_type_count,
    coalesce(auto_typ.cnt, 0) as auto_url_type_count,
    coalesce(user_ag.cnt, 0) as user_agency_count,
    coalesce(user_loc.cnt, 0) as user_location_count,
    coalesce(user_rec.cnt, 0) as user_record_type_count,
    coalesce(user_typ.cnt, 0) as user_url_type_count,
    (
    coalesce(auto_ag.cnt, 0) +
    coalesce(auto_loc.cnt, 0) +
    coalesce(auto_rec.cnt, 0) +
    coalesce(auto_typ.cnt, 0) +
    coalesce(user_ag.cnt, 0) +
    coalesce(user_loc.cnt, 0) +
    coalesce(user_rec.cnt, 0) +
    coalesce(user_typ.cnt, 0)
    ) as total_anno_count

    from urls u
    left join auto_agency_count auto_ag on auto_ag.id = u.id
    left join auto_location_count auto_loc on auto_loc.id = u.id
    left join auto_record_type_count auto_rec on auto_rec.id = u.id
    left join auto_url_type_count auto_typ on auto_typ.id = u.id
    left join user_agency_count user_ag on user_ag.id = u.id
    left join user_location_count user_loc on user_loc.id = u.id
    left join user_record_type_count user_rec on user_rec.id = u.id
    left join user_url_type_count user_typ on user_typ.id = u.id

    
    """)


def upgrade() -> None:
    _drop_meta_url_view()
    _drop_unvalidated_url_view()

    # URL Type
    _rename_validated_url_type_to_url_type()
    _add_not_found_url_type()

    # suggested Status
    _rename_user_relevant_suggestions_to_user_url_type_suggestions()
    _rename_suggested_status_column_to_type()
    _switch_suggested_status_with_url_type()
    _remove_suggested_status_enum()

    _add_flag_url_auto_validated_table()
    _add_auto_validate_task()

    _create_anno_count_view()


    _add_meta_url_view()
    _add_unvalidated_url_view()


def _remove_suggested_status_enum():
    op.execute(f"DROP TYPE suggested_status")


def _add_suggested_status_enum():
    op.execute(
        "create type suggested_status as enum " +
        "('relevant', 'not relevant', 'individual record', 'broken page/404 not found');"
    )


def _drop_anno_count_view():
    op.execute("""
    DROP VIEW IF EXISTS url_annotation_count_view
    """)


def downgrade() -> None:
    _drop_meta_url_view()
    _drop_unvalidated_url_view()
    _drop_anno_count_view()

    # Suggested Status
    _add_suggested_status_enum()
    _replace_url_type_with_suggested_status()
    _rename_type_column_to_suggested_status()
    _rename_user_url_type_suggestions_to_user_relevant_suggestions()

    # URL Type
    _remove_not_found_url_type()
    _rename_url_type_to_validated_url_type()

    _remove_auto_validate_task()
    _remove_flag_url_auto_validated_table()


    _add_meta_url_view()
    _add_unvalidated_url_view()

def _rename_suggested_status_column_to_type():
    op.alter_column(
        table_name=USER_URL_TYPE_SUGGESTIONS_TABLE_NAME,
        column_name='suggested_status',
        new_column_name='type'
    )


def _rename_type_column_to_suggested_status():
    op.alter_column(
        table_name=USER_URL_TYPE_SUGGESTIONS_TABLE_NAME,
        column_name='type',
        new_column_name='suggested_status'
    )




def _drop_unvalidated_url_view():
    op.execute("DROP VIEW IF EXISTS unvalidated_url_view")


def _add_unvalidated_url_view():
    op.execute("""
        CREATE OR REPLACE VIEW unvalidated_url_view AS
        select
            u.id as url_id
        from
            urls u
            left join flag_url_validated fuv
                      on fuv.url_id = u.id
        where
            fuv.type is null
    """)


def _add_meta_url_view():
    op.execute("""
    CREATE OR REPLACE VIEW meta_url_view AS
        SELECT
            urls.id as url_id
        FROM urls
        INNER JOIN flag_url_validated fuv on fuv.url_id = urls.id
        where fuv.type = 'meta url'
    """)

def _drop_meta_url_view():
    op.execute("DROP VIEW IF EXISTS meta_url_view")

def _rename_validated_url_type_to_url_type():
    op.execute(f"""
    ALTER TYPE {VALIDATED_URL_TYPE_NAME} RENAME TO {URL_TYPE_NAME}
    """)

def _rename_url_type_to_validated_url_type():
    op.execute(f"""
    ALTER TYPE {URL_TYPE_NAME} RENAME TO {VALIDATED_URL_TYPE_NAME}
    """)

def _add_not_found_url_type():
    switch_enum_type(
        table_name=FLAG_URL_VALIDATED_TABLE_NAME,
        column_name='type',
        enum_name=URL_TYPE_NAME,
        new_enum_values=[
            'data source',
            'meta url',
            'not relevant',
            'individual record',
            'not found'
        ]
    )

def _remove_not_found_url_type():
    switch_enum_type(
        table_name=FLAG_URL_VALIDATED_TABLE_NAME,
        column_name='type',
        enum_name=URL_TYPE_NAME,
        new_enum_values=[
            'data source',
            'meta url',
            'not relevant',
            'individual record'
        ]
    )


def _switch_suggested_status_with_url_type():
    op.execute(f"""
    ALTER TABLE {USER_URL_TYPE_SUGGESTIONS_TABLE_NAME}
    ALTER COLUMN type type {URL_TYPE_NAME}
    USING (
        CASE  type::text
            WHEN 'relevant' THEN 'data source'
            WHEN 'broken page/404 not found' THEN 'not found'
        ELSE type::text
        END
    )::{URL_TYPE_NAME}
    """)



def _replace_url_type_with_suggested_status():
    op.execute(f"""
    ALTER TABLE {USER_URL_TYPE_SUGGESTIONS_TABLE_NAME}
    ALTER COLUMN type type suggested_status
    USING (
        CASE type::text
            WHEN 'data source' THEN 'relevant'
            WHEN 'not found' THEN 'broken page/404 not found'
        ELSE type::text
        END
    )::suggested_status

    """)




def _add_flag_url_auto_validated_table():
    op.create_table(
        FLAG_URL_AUTO_VALIDATED_TABLE_NAME,
        url_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint('url_id')
    )



def _remove_flag_url_auto_validated_table():
    op.drop_table(FLAG_URL_AUTO_VALIDATED_TABLE_NAME)



def _add_auto_validate_task():
    switch_enum_type(
        table_name='tasks',
        column_name='task_type',
        enum_name='task_type',
        new_enum_values=[
            'HTML',
            'Relevancy',
            'Record Type',
            'Agency Identification',
            'Misc Metadata',
            'Submit Approved URLs',
            'Duplicate Detection',
            '404 Probe',
            'Sync Agencies',
            'Sync Data Sources',
            'Push to Hugging Face',
            'URL Probe',
            'Populate Backlog Snapshot',
            'Delete Old Logs',
            'Run URL Task Cycles',
            'Root URL',
            'Internet Archives Probe',
            'Internet Archives Archive',
            'Screenshot',
            'Location ID',
            AUTO_VALIDATION_TASK_TYPE,
        ]
    )


def _rename_user_relevant_suggestions_to_user_url_type_suggestions():
    op.rename_table(
        old_table_name=USER_RELEVANT_SUGGESTIONS_TABLE_NAME,
        new_table_name=USER_URL_TYPE_SUGGESTIONS_TABLE_NAME
    )



def _rename_user_url_type_suggestions_to_user_relevant_suggestions():
    op.rename_table(
        old_table_name=USER_URL_TYPE_SUGGESTIONS_TABLE_NAME,
        new_table_name=USER_RELEVANT_SUGGESTIONS_TABLE_NAME
    )


def _remove_auto_validate_task():
    switch_enum_type(
        table_name='tasks',
        column_name='task_type',
        enum_name='task_type',
        new_enum_values=[
            'HTML',
            'Relevancy',
            'Record Type',
            'Agency Identification',
            'Misc Metadata',
            'Submit Approved URLs',
            'Duplicate Detection',
            '404 Probe',
            'Sync Agencies',
            'Sync Data Sources',
            'Push to Hugging Face',
            'URL Probe',
            'Populate Backlog Snapshot',
            'Delete Old Logs',
            'Run URL Task Cycles',
            'Root URL',
            'Internet Archives Probe',
            'Internet Archives Archive',
            'Screenshot',
            'Location ID'
        ]
    )


