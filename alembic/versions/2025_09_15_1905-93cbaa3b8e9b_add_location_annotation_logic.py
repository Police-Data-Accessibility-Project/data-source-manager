"""Add location annotation logic

Revision ID: 93cbaa3b8e9b
Revises: d5f92e6fedf4
Create Date: 2025-09-15 19:05:27.872875

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from src.util.alembic_helpers import switch_enum_type, url_id_column, location_id_column, created_at_column, id_column, \
    task_id_column, user_id_column

# revision identifiers, used by Alembic.
revision: str = '93cbaa3b8e9b'
down_revision: Union[str, None] = 'd5f92e6fedf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

USER_LOCATION_SUGGESTIONS_TABLE_NAME = 'user_location_suggestions'
AUTO_LOCATION_ID_SUBTASK_TABLE_NAME = 'auto_location_id_subtasks'
LOCATION_ID_SUBTASK_SUGGESTIONS_TABLE_NAME = 'location_id_subtask_suggestions'
LOCATION_ID_TASK_TYPE = 'Location ID'
LOCATION_ID_SUBTASK_TYPE_NAME = 'location_id_subtask_type'




def upgrade() -> None:
    _add_location_id_task_type()
    _create_user_location_suggestions_table()
    _create_auto_location_id_subtask_table()
    _create_location_id_subtask_suggestions_table()
    _create_new_url_annotation_flags_view()
    _create_locations_expanded_view()
    _create_state_location_trigger()
    _create_county_location_trigger()
    _create_locality_location_trigger()
    _add_pg_trgm_extension()

def downgrade() -> None:
    _drop_locations_expanded_view()
    _create_old_url_annotation_flags_view()
    _drop_location_id_subtask_suggestions_table()
    _drop_auto_location_id_subtask_table()
    _drop_user_location_suggestions_table()
    _drop_location_id_task_type()
    _drop_location_id_subtask_type()
    _drop_state_location_trigger()
    _drop_county_location_trigger()
    _drop_locality_location_trigger()
    _drop_pg_trgm_extension()

def _drop_pg_trgm_extension():
    op.execute("""
    drop extension if exists pg_trgm;
        """)

def _add_pg_trgm_extension():
    op.execute("""
    create extension if not exists pg_trgm;
    """)


def _create_state_location_trigger():
    # Function
    op.execute("""
    create function insert_state_location() returns trigger
        language plpgsql
    as
    $$
    BEGIN
        -- Insert a new location of type 'State' when a new state is added
        INSERT INTO locations (type, state_id)
        VALUES ('State', NEW.id);
        RETURN NEW;
    END;
    $$; 
    """)

    # Trigger
    op.execute("""
    create trigger after_state_insert
    after insert
    on us_states
    for each row
    execute procedure insert_state_location();
    """)


def _create_county_location_trigger():
    # Function
    op.execute("""
    create function insert_county_location() returns trigger
        language plpgsql
    as
    $$
    BEGIN
        -- Insert a new location of type 'County' when a new county is added
        INSERT INTO locations (type, state_id, county_id)
        VALUES ('County', NEW.state_id, NEW.id);
        RETURN NEW;
    END;
    $$;
    """)

    # Trigger
    op.execute("""
    create trigger after_county_insert
        after insert
        on counties
        for each row
    execute procedure insert_county_location();
    """)


def _create_locality_location_trigger():
    # Function
    op.execute("""
    create function insert_locality_location() returns trigger
        language plpgsql
    as
    $$
    DECLARE
        v_state_id BIGINT;
    BEGIN
        -- Get the state_id from the associated county
        SELECT c.state_id INTO v_state_id
        FROM counties c
        WHERE c.id = NEW.county_id;
    
        -- Insert a new location of type 'Locality' when a new locality is added
        INSERT INTO locations (type, state_id, county_id, locality_id)
        VALUES ('Locality', v_state_id, NEW.county_id, NEW.id);
    
        RETURN NEW;
    END;
    $$;
    """)

    # Trigger
    op.execute("""
    create trigger after_locality_insert
        after insert
        on localities
        for each row
    execute procedure insert_locality_location();

    """)


def _drop_state_location_trigger():
    # Trigger
    op.execute("""
    drop trigger if exists after_state_insert on us_states;
    """)

    # Function
    op.execute("""
    drop function if exists insert_state_location;
    """)




def _drop_locality_location_trigger():
    # Trigger
    op.execute("""
    drop trigger if exists after_locality_insert on localities;
    """)

    # Function
    op.execute("""
    drop function if exists insert_locality_location;
    """)



def _drop_county_location_trigger():
    # Trigger
    op.execute("""
    drop trigger if exists after_county_insert on counties;
    """)

    # Function
    op.execute("""
    drop function if exists insert_county_location;
    """)



def _create_new_url_annotation_flags_view():
    op.execute("""DROP VIEW IF EXISTS url_annotation_flags;""")
    op.execute(
        f"""
        CREATE OR REPLACE VIEW url_annotation_flags AS
        (
        SELECT u.id as url_id,
                EXISTS (SELECT 1 FROM public.auto_record_type_suggestions    a WHERE a.url_id = u.id) AS has_auto_record_type_suggestion,
                EXISTS (SELECT 1 FROM public.auto_relevant_suggestions       a WHERE a.url_id = u.id) AS has_auto_relevant_suggestion,
                EXISTS (SELECT 1 FROM public.url_auto_agency_id_subtasks     a WHERE a.url_id = u.id) AS has_auto_agency_suggestion,
                EXISTS (SELECT 1 FROM public.auto_location_id_subtasks       a WHERE a.url_id = u.id) AS has_auto_location_suggestion,
                EXISTS (SELECT 1 FROM public.user_record_type_suggestions    a WHERE a.url_id = u.id) AS has_user_record_type_suggestion,
                EXISTS (SELECT 1 FROM public.user_relevant_suggestions       a WHERE a.url_id = u.id) AS has_user_relevant_suggestion,
                EXISTS (SELECT 1 FROM public.user_url_agency_suggestions     a WHERE a.url_id = u.id) AS has_user_agency_suggestion,
                EXISTS (SELECT 1 FROM public.user_location_suggestions       a WHERE a.url_id = u.id) AS has_user_location_suggestion,
                EXISTS (SELECT 1 FROM public.link_urls_agency                a WHERE a.url_id = u.id) AS has_confirmed_agency,
                EXISTS (SELECT 1 FROM public.reviewing_user_url              a WHERE a.url_id = u.id) AS was_reviewed
        FROM urls u
            )
        """
    )

def _create_old_url_annotation_flags_view():
    op.execute("""DROP VIEW IF EXISTS url_annotation_flags;""")
    op.execute(
        f"""
        CREATE OR REPLACE VIEW url_annotation_flags AS
        (
        SELECT u.id as url_id,
                EXISTS (SELECT 1 FROM public.auto_record_type_suggestions    a WHERE a.url_id = u.id) AS has_auto_record_type_suggestion,
                EXISTS (SELECT 1 FROM public.auto_relevant_suggestions       a WHERE a.url_id = u.id) AS has_auto_relevant_suggestion,
                EXISTS (SELECT 1 FROM public.url_auto_agency_id_subtasks     a WHERE a.url_id = u.id) AS has_auto_agency_suggestion,
                EXISTS (SELECT 1 FROM public.user_record_type_suggestions    a WHERE a.url_id = u.id) AS has_user_record_type_suggestion,
                EXISTS (SELECT 1 FROM public.user_relevant_suggestions       a WHERE a.url_id = u.id) AS has_user_relevant_suggestion,
                EXISTS (SELECT 1 FROM public.user_url_agency_suggestions     a WHERE a.url_id = u.id) AS has_user_agency_suggestion,
                EXISTS (SELECT 1 FROM public.link_urls_agency                a WHERE a.url_id = u.id) AS has_confirmed_agency,
                EXISTS (SELECT 1 FROM public.reviewing_user_url              a WHERE a.url_id = u.id) AS was_reviewed
        FROM urls u
            )
        """
    )


def _drop_locations_expanded_view():
    op.execute("""
    drop view if exists public.locations_expanded;
    """)

def _create_locations_expanded_view():
    op.execute("""
    create or replace view public.locations_expanded
        (id, type, state_name, state_iso, county_name, county_fips, locality_name, locality_id, state_id, county_id,
         display_name, full_display_name)
    as
    SELECT
        locations.id,
        locations.type,
        us_states.state_name,
        us_states.state_iso,
        counties.name   AS county_name,
        counties.fips   AS county_fips,
        localities.name AS locality_name,
        localities.id   AS locality_id,
        us_states.id    AS state_id,
        counties.id     AS county_id,
        CASE
            WHEN locations.type = 'Locality'::location_type THEN localities.name
            WHEN locations.type = 'County'::location_type THEN counties.name::character varying
            WHEN locations.type = 'State'::location_type THEN us_states.state_name::character varying
            ELSE NULL::character varying
            END         AS display_name,
        CASE
            WHEN locations.type = 'Locality'::location_type THEN concat(localities.name, ', ', counties.name, ', ',
                                                                        us_states.state_name)::character varying
            WHEN locations.type = 'County'::location_type
                THEN concat(counties.name, ', ', us_states.state_name)::character varying
            WHEN locations.type = 'State'::location_type THEN us_states.state_name::character varying
            ELSE NULL::character varying
            END         AS full_display_name
    FROM
        locations
            LEFT JOIN us_states ON locations.state_id = us_states.id
            LEFT JOIN counties ON locations.county_id = counties.id
            LEFT JOIN localities ON locations.locality_id = localities.id;
        
    """)

def _add_location_id_task_type():
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
            LOCATION_ID_TASK_TYPE
        ]
    )


def _create_user_location_suggestions_table():
    op.create_table(
        USER_LOCATION_SUGGESTIONS_TABLE_NAME,
        url_id_column(),
        user_id_column(),
        location_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint(
            'url_id',
            'user_id',
            'location_id',
            name='user_location_suggestions_pk'
        )
    )


def _create_auto_location_id_subtask_table():
    op.create_table(
        AUTO_LOCATION_ID_SUBTASK_TABLE_NAME,
        id_column(),
        task_id_column(),
        url_id_column(),
        sa.Column(
            'locations_found',
            sa.Boolean(),
            nullable=False
        ),
        sa.Column(
            'type',
            sa.Enum(
                'nlp_location_frequency',
                name='auto_location_id_subtask_type'
            ),
            nullable=False
        ),
        created_at_column(),
        sa.UniqueConstraint(
            'url_id',
            'type',
            name='auto_location_id_subtask_url_id_type_unique'
        )
    )


def _create_location_id_subtask_suggestions_table():
    op.create_table(
        LOCATION_ID_SUBTASK_SUGGESTIONS_TABLE_NAME,
        sa.Column(
            'subtask_id',
            sa.Integer(),
            sa.ForeignKey(
                f'{AUTO_LOCATION_ID_SUBTASK_TABLE_NAME}.id',
                ondelete='CASCADE'
            ),
        ),
        location_id_column(),
        sa.Column(
            'confidence',
            sa.Float(),
            nullable=False
        ),
        created_at_column(),
        sa.PrimaryKeyConstraint(
            'subtask_id',
            'location_id',
            name='location_id_subtask_suggestions_pk'
        )
    )



def _drop_location_id_task_type():
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
        ]
    )


def _drop_auto_location_id_subtask_table():
    op.drop_table(AUTO_LOCATION_ID_SUBTASK_TABLE_NAME)


def _drop_user_location_suggestions_table():
    op.drop_table(USER_LOCATION_SUGGESTIONS_TABLE_NAME)


def _drop_location_id_subtask_suggestions_table():
    op.drop_table(LOCATION_ID_SUBTASK_SUGGESTIONS_TABLE_NAME)

def _drop_location_id_subtask_type():
    op.execute("""
    DROP TYPE IF EXISTS auto_location_id_subtask_type;
    """)

