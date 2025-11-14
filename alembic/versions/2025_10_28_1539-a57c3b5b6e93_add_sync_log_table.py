"""Add sync_log table

Revision ID: a57c3b5b6e93
Revises: f32ba7664e9f
Create Date: 2025-10-28 15:39:50.494489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import created_at_column, updated_at_column, create_updated_at_trigger, remove_enum_value

# revision identifiers, used by Alembic.
revision: str = 'a57c3b5b6e93'
down_revision: Union[str, None] = 'f32ba7664e9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_data_portal_type_other_to_ds_optional_metadata():
    op.add_column(
        'url_optional_data_source_metadata',
        sa.Column(
            'data_portal_type_other',
            sa.String(),
            nullable=True
        )
    )


def upgrade() -> None:
    _create_sync_log()
    _create_ds_agency_link()
    _migrate_agency_ids_to_ds_agency_link()
    remove_id_column_from_agencies()
    rename_agency_id_to_id()
    _rename_existing_tables_to_ds_app_format()
    _alter_ds_app_link_data_source_table()
    _alter_ds_app_link_meta_url_table()
    _add_flag_deletion_tables()
    _add_last_synced_at_columns()
    _add_link_table_modification_triggers()
    _add_updated_at_to_optional_data_source_metadata_table()
    _update_sync_tasks()
    _alter_agency_jurisdiction_type_column()
    _add_updated_at_to_url_record_type_table()
    _add_updated_at_trigger_to_url_optional_data_source_metadata()
    _add_data_portal_type_other_to_ds_optional_metadata()

def _add_updated_at_trigger_to_url_optional_data_source_metadata():
    create_updated_at_trigger(
        "url_optional_data_source_metadata"
    )

def _add_updated_at_to_url_record_type_table():
    op.add_column(
        'url_record_type',
        updated_at_column()
    )
    create_updated_at_trigger(
        "url_record_type"
    )



def _alter_agency_jurisdiction_type_column():
    op.alter_column(
        'agencies',
        'jurisdiction_type',
        nullable=False,
    )


def _update_sync_tasks():

    # Drop Views
    op.execute("drop view url_task_count_1_day")
    op.execute("drop view url_task_count_1_week")
    op.execute("drop materialized view url_status_mat_view")



    targets: list[tuple[str, str]] = [
        ('tasks', 'task_type'),
        ('url_task_error', 'task_type')
    ]

    remove_enum_value(
        enum_name="task_type",
        value_to_remove="Sync Agencies",
        targets=targets
    )
    remove_enum_value(
        enum_name="task_type",
        value_to_remove="Sync Data Sources",
        targets=targets
    )
    new_enum_values: list[str] = [
        "Sync Agencies Add",
        "Sync Agencies Update",
        "Sync Agencies Delete",
        "Sync Data Sources Add",
        "Sync Data Sources Update",
        "Sync Data Sources Delete",
        "Sync Meta URLs Add",
        "Sync Meta URLs Update",
        "Sync Meta URLs Delete",
    ]
    for enum_value in new_enum_values:
        op.execute(f"ALTER TYPE task_type ADD VALUE '{enum_value}';")

    # Recreate Views
    op.execute("""
    create view url_task_count_1_day(task_type, count) as
    SELECT
        t.task_type,
        count(ltu.url_id) AS count
    FROM
        tasks t
        JOIN link_task_urls ltu
             ON ltu.task_id = t.id
    WHERE
        t.updated_at > (now() - '1 day'::interval)
    GROUP BY
        t.task_type;
    """)

    op.execute("""
    create view url_task_count_1_week(task_type, count) as
    SELECT
        t.task_type,
        count(ltu.url_id) AS count
    FROM
        tasks t
        JOIN link_task_urls ltu
             ON ltu.task_id = t.id
    WHERE
        t.updated_at > (now() - '7 days'::interval)
    GROUP BY
        t.task_type;    
    """)

    op.execute(
        """
    CREATE MATERIALIZED VIEW url_status_mat_view as
        with
        urls_with_relevant_errors as (
            select
                ute.url_id
            from
                url_task_error ute
            where
                ute.task_type in (
                                  'Screenshot',
                                  'HTML',
                                  'URL Probe'
                    )
            )
        , status_text as (
            select
                u.id as url_id,
                case
                    when (
                        -- Validated as not relevant, individual record, or not found
                        fuv.type in ('not relevant', 'individual record', 'not found')
                        ) Then 'Accepted'
                    when (
                        (fuv.type = 'data source' and uds.url_id is null)
                            OR
                        (fuv.type = 'meta url' and udmu.url_id is null)
                        ) Then 'Awaiting Submission'
                    when (
                        (fuv.type = 'data source' and uds.url_id is not null)
                            OR
                        (fuv.type = 'meta url' and udmu.url_id is not null)
                        ) Then 'Submitted'
                    when (
                        -- Has compressed HTML
                        uch.url_id is not null
                            AND
                            -- Has web metadata
                        uwm.url_id is not null
                            AND
                            -- Has screenshot
                        us.url_id is not null
                        ) THEN 'Community Labeling'
                    when uwre.url_id is not null then 'Error'
                    ELSE 'Intake'
                    END as status
    
            from
                urls u
                left join urls_with_relevant_errors uwre
                          on u.id = uwre.url_id
                left join url_screenshot us
                          on u.id = us.url_id
                left join url_compressed_html uch
                          on u.id = uch.url_id
                left join url_web_metadata uwm
                          on u.id = uwm.url_id
                left join flag_url_validated fuv
                          on u.id = fuv.url_id
                left join ds_app_link_meta_url udmu
                          on u.id = udmu.url_id
                left join ds_app_link_data_source uds
                          on u.id = uds.url_id
        )
    select
        url_id,
        status,
        CASE status
            WHEN 'Intake' THEN 100
            WHEN 'Error' THEN 110
            WHEN 'Community Labeling' THEN 200
            WHEN 'Accepted' THEN 300
            WHEN 'Awaiting Submission' THEN 380
            WHEN 'Submitted' THEN 390
            ELSE -1
        END as code
    from status_text
    """
        )


def last_synced_at_column():
    return sa.Column(
        'last_synced_at',
        sa.DateTime(),
        nullable=False,
        server_default=sa.func.now()
    )


def _add_link_table_modification_triggers():
    op.execute("""
    -- trigger func that "touches" parent rows hit by changes to the link table
    CREATE OR REPLACE FUNCTION touch_url_from_agency_link()
    RETURNS trigger
    LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP = 'INSERT' THEN
        EXECUTE $q$
          UPDATE urls u
          SET updated_at = clock_timestamp()
          FROM (SELECT DISTINCT url_id FROM newtab) AS hit
          WHERE u.id = hit.url_id
        $q$;
    
      ELSIF TG_OP = 'DELETE' THEN
        EXECUTE $q$
          UPDATE urls u
          SET updated_at = clock_timestamp()
          FROM (SELECT DISTINCT url_id FROM oldtab) AS hit
          WHERE u.id = hit.url_id
        $q$;
    
      ELSE  -- UPDATE
        EXECUTE $q$
          UPDATE urls u
          SET updated_at = clock_timestamp()
          FROM (
            SELECT DISTINCT url_id FROM newtab
            UNION
            SELECT DISTINCT url_id FROM oldtab
          ) AS hit
          WHERE u.id = hit.url_id
        $q$;
      END IF;
    
      RETURN NULL; -- statement-level trigger
    END $$;
    
    -- statement-level trigger with transition tables
    CREATE TRIGGER trg_link_urls_agency_touch_url_ins
    AFTER INSERT ON link_urls_agency
    REFERENCING NEW TABLE AS newtab
    FOR EACH STATEMENT
    EXECUTE FUNCTION touch_url_from_agency_link();
    
    CREATE TRIGGER trg_link_urls_agency_touch_url_upd
    AFTER UPDATE ON link_urls_agency
    REFERENCING NEW TABLE AS newtab OLD TABLE AS oldtab
    FOR EACH STATEMENT
    EXECUTE FUNCTION touch_url_from_agency_link();
    
    CREATE TRIGGER trg_link_urls_agency_touch_url_del
    AFTER DELETE ON link_urls_agency
    REFERENCING OLD TABLE AS oldtab
    FOR EACH STATEMENT
    EXECUTE FUNCTION touch_url_from_agency_link();
    
    """)

    op.execute(
        """
        -- trigger func that "touches" agency rows hit by changes to the link_agencies_locations table
        CREATE OR REPLACE FUNCTION touch_agency_from_location_link()
            RETURNS trigger
            LANGUAGE plpgsql AS
        $$
        BEGIN
          IF TG_OP = 'INSERT' THEN
            EXECUTE $q$
              UPDATE agencies a
              SET updated_at = clock_timestamp()
              FROM (SELECT DISTINCT agency_id FROM newtab) AS hit
              WHERE a.id = hit.agency_id
            $q$;
        
          ELSIF TG_OP = 'DELETE' THEN
            EXECUTE $q$
              UPDATE agencies a
              SET updated_at = clock_timestamp()
              FROM (SELECT DISTINCT agency_id FROM oldtab) AS hit
              WHERE a.id = hit.agency_id
            $q$;
        
          ELSE  -- UPDATE
            EXECUTE $q$
              UPDATE agencies a
              SET updated_at = clock_timestamp()
              FROM (
                SELECT DISTINCT agency_id FROM newtab
                UNION
                SELECT DISTINCT agency_id FROM oldtab
              ) AS hit
              WHERE a.id = hit.agency_id
            $q$;
          END IF;
        
          RETURN NULL; -- statement-level trigger
        END
        $$;

        -- statement-level trigger with transition tables
        CREATE TRIGGER trg_link_agencies_locations_touch_agencies_ins
        AFTER INSERT ON link_agencies_locations
        REFERENCING NEW TABLE AS newtab
        FOR EACH STATEMENT
        EXECUTE FUNCTION touch_agency_from_location_link();
        
        CREATE TRIGGER trg_link_agencies_locations_touch_agencies_upd
        AFTER UPDATE ON link_agencies_locations
        REFERENCING NEW TABLE AS newtab OLD TABLE AS oldtab
        FOR EACH STATEMENT
        EXECUTE FUNCTION touch_agency_from_location_link();
        
        CREATE TRIGGER trg_link_agencies_locations_touch_agencies_del
        AFTER DELETE ON link_agencies_locations
        REFERENCING OLD TABLE AS oldtab
        FOR EACH STATEMENT
        EXECUTE FUNCTION touch_agency_from_location_link();
               """
    )







def _add_updated_at_to_optional_data_source_metadata_table():
    op.add_column(
        "url_optional_data_source_metadata",
        updated_at_column()
    )
    create_updated_at_trigger(
        "url_optional_data_source_metadata"
    )

def _add_last_synced_at_columns():
    op.add_column(
        'ds_app_link_data_source',
        last_synced_at_column()
    )
    op.add_column(
        'ds_app_link_meta_url',
        last_synced_at_column()
    )


def _alter_ds_app_link_data_source_table():
    # Drop unique constraint for data source id
    op.drop_constraint(
        'uq_url_data_sources_data_source_id',
        'ds_app_link_data_source',
        type_='unique'
    )
    # Drop primary keys
    op.drop_constraint(
        'url_data_sources_pkey',
        'ds_app_link_data_source',
        type_='primary'
    )
    # Rename `data_source_id` to `ds_data_source_id`
    op.alter_column(
        'ds_app_link_data_source',
        'data_source_id',
        new_column_name='ds_data_source_id',
    )
    # Add new primary key
    op.create_primary_key(
        'ds_app_link_data_source_pkey',
        'ds_app_link_data_source',
        ['ds_data_source_id']
    )

    # Drop url_id foreign key
    op.drop_constraint(
        'url_data_sources_url_id_fkey',
        'ds_app_link_data_source',
        type_='foreignkey'
    )
    # Recreate foreign key with ON DELETE SET NULL
    op.create_foreign_key(
        'ds_app_link_data_source_url_id_fkey',
        'ds_app_link_data_source',
        'urls',
        ['url_id'],
        ['id'],
        ondelete='SET NULL'
    )
    # Alter url_id column to be nullable
    op.alter_column(
        'ds_app_link_data_source',
        'url_id',
        nullable=True
    )



def _alter_ds_app_link_meta_url_table():
    # Drop joint primary key for url_id and agency_id
    op.drop_constraint(
        'url_ds_meta_url_pkey',
        'ds_app_link_meta_url',
        type_='primary'
    )
    # Drop unique constraint for ds_meta_url_id
    op.drop_constraint(
        'url_ds_meta_url_ds_meta_url_id_key',
        'ds_app_link_meta_url',
        type_='unique'
    )
    # Drop agency_id column
    op.drop_column(
        'ds_app_link_meta_url',
        'agency_id'
    )
    # Make ds_meta_url_id primary key
    op.create_primary_key(
        'ds_app_link_meta_url_pkey',
        'ds_app_link_meta_url',
        ['ds_meta_url_id']
    )
    # Add unique constraint for url_id
    op.create_unique_constraint(
        'uq_ds_app_link_meta_url_url_id',
        'ds_app_link_meta_url',
        ['url_id']
    )
    # URL ID
    ## Drop foreign key
    op.drop_constraint(
        'url_ds_meta_url_url_id_fkey',
        'ds_app_link_meta_url',
        type_='foreignkey'
    )
    ## Recreate foreign key with ON DELETE SET NULL
    op.create_foreign_key(
        'ds_app_link_meta_url_url_id_fkey',
        'ds_app_link_meta_url',
        'urls',
        ['url_id'],
        ['id'],
        ondelete='SET NULL'
    )
    ## Alter url_id column to be nullable
    op.alter_column(
        'ds_app_link_meta_url',
        'url_id',
        nullable=True
    )


def _add_flag_deletion_tables():
    op.create_table(
        'flag_ds_delete_agency',
        sa.Column(
            'ds_agency_id',
            sa.Integer(),
            sa.ForeignKey(
                'ds_app_link_agency.ds_agency_id',
                ondelete='CASCADE'
            ),
            primary_key=True,
            nullable=False
        ),
        created_at_column()
    )

    op.create_table(
        'flag_ds_delete_data_source',
        sa.Column(
            'ds_data_source_id',
            sa.Integer(),
            sa.ForeignKey(
                'ds_app_link_data_source.ds_data_source_id',
                ondelete='CASCADE'
            ),
            primary_key=True,
            nullable=False
        ),
        created_at_column(),
    )

    op.create_table(
        'flag_ds_delete_meta_url',
        sa.Column(
            'ds_meta_url_id',
            sa.Integer(),
            sa.ForeignKey(
                'ds_app_link_meta_url.ds_meta_url_id',
                ondelete='CASCADE'
            ),
            primary_key=True,
            nullable=False
        ),
        created_at_column(),
    )


def _rename_existing_tables_to_ds_app_format():
    op.rename_table(
        'url_data_source',
        'ds_app_link_data_source'
    )
    op.rename_table(
        'url_ds_meta_url',
        'ds_app_link_meta_url'
    )

def _migrate_agency_ids_to_ds_agency_link():
    """
    While this migration uses the existing DS agency IDs for both sm and ds agency ids
    From this point onward the sm ID is internal to the SM application,
    and the same is true for DS ID.
    """

    op.execute("""
    INSERT INTO ds_app_link_agency(agency_id, ds_agency_id)
        SELECT agency_id, agency_id
        FROM agencies
    """)


def remove_id_column_from_agencies():
    op.drop_column(
        'agencies',
        'id'
    )

def rename_agency_id_to_id():
    op.alter_column(
        'agencies',
        'agency_id',
        new_column_name='id'
    )

def _create_ds_agency_link():
    op.create_table(
        'ds_app_link_agency',
        sa.Column(
            'agency_id',
            sa.Integer(),
            sa.ForeignKey(
                'agencies.agency_id',
                ondelete='SET NULL'
            ),
            nullable=True
        ),
        sa.Column(
            'ds_agency_id',
            sa.Integer(),
            nullable=False,
            primary_key=True
        ),
        created_at_column(),
        last_synced_at_column(),
        sa.UniqueConstraint(
            "agency_id", name="uq_ds_app_link_agency_agency_id"
        )
    )


def _create_sync_log():
    op.create_table(
        'sync_log',
        sa.Column(
            'resource_type',
            sa.Enum(
                'agency',
                'data_source',
                'meta_url',
                name='resource_type_enum'
            ),
            nullable=False,
        ),
        sa.Column(
            'sync_type',
            sa.Enum(
                'add',
                'update',
                'delete',
                name='sync_type_enum'
            ),
            nullable=False,
        ),
        sa.Column(
            'count',
            sa.Integer(),
            nullable=False,
        ),
        created_at_column(),
        sa.PrimaryKeyConstraint(
            'resource_type',
            'sync_type',
            'created_at'
        )
    )


def downgrade() -> None:
    pass
