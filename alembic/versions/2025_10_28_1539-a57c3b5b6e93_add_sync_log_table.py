"""Add sync_log table

Revision ID: a57c3b5b6e93
Revises: f32ba7664e9f
Create Date: 2025-10-28 15:39:50.494489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import created_at_column

# revision identifiers, used by Alembic.
revision: str = 'a57c3b5b6e93'
down_revision: Union[str, None] = 'f32ba7664e9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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
      -- UNION to cover INSERT/UPDATE (NEW TABLE) and DELETE (OLD TABLE)
      UPDATE urls u
      SET updated_at = clock_timestamp()  -- better than now() for long txns
      FROM (
        SELECT DISTINCT url_id FROM newtab
        UNION
        SELECT DISTINCT url_id FROM oldtab
      ) AS hit
      WHERE u.id = hit.url_id;
    
      RETURN NULL; -- statement-level trigger
    END $$;
    
    -- statement-level trigger with transition tables
    CREATE TRIGGER trg_link_touch_parent
    AFTER INSERT OR UPDATE OR DELETE ON link_parent_child
    REFERENCING NEW TABLE AS newtab OLD TABLE AS oldtab
    FOR EACH STATEMENT
    EXECUTE FUNCTION touch_parent_from_link();
    
    """)

    op.execute(
        """
        -- trigger func that "touches" agency rows hit by changes to the link_agencies_locations table
        CREATE OR REPLACE FUNCTION touch_agency_from_location_link()
            RETURNS trigger
            LANGUAGE plpgsql AS
        $$
        BEGIN
            -- UNION to cover INSERT/UPDATE (NEW TABLE) and DELETE (OLD TABLE)
            UPDATE agencies a
            SET updated_at = clock_timestamp() -- better than now() for long txns
            FROM (SELECT DISTINCT agency_id
                  FROM newtab
                  UNION
                  SELECT DISTINCT agency_id
                  FROM oldtab) AS hit
            WHERE a.id = hit.agency_id;

            RETURN NULL; -- statement-level trigger
        END
        $$;

        -- statement-level trigger with transition tables
        CREATE TRIGGER trg_link_touch_parent
            AFTER INSERT OR UPDATE OR DELETE
            ON link_agencies_locations
            REFERENCING NEW TABLE AS newtab OLD TABLE AS oldtab
            FOR EACH STATEMENT
        EXECUTE FUNCTION touch_agency_from_location_link();
               """
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
