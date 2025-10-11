from alembic import op
import sqlalchemy as sa

def switch_enum_type(
        table_name,
        column_name,
        enum_name,
        new_enum_values,
        drop_old_enum=True,
        check_constraints_to_drop: list[str] = None,
        conversion_mappings: dict[str, str] = None
):
    """
    Switches an ENUM type in a PostgreSQL column by:
    1. Renaming the old enum type.
    2. Creating the new enum type with the same name.
    3. Updating the column to use the new enum type.
    4. Dropping the old enum type.

    :param table_name: Name of the table containing the ENUM column.
    :param column_name: Name of the column using the ENUM type.
    :param enum_name: Name of the ENUM type in PostgreSQL.
    :param new_enum_values: List of new ENUM values.
    :param drop_old_enum: Whether to drop the old ENUM type.
    :param check_constraints_to_drop: List of check constraints to drop before switching the ENUM type.
    :param conversion_mappings: Dictionary of old values to new values for the ENUM type.
    """

    # 1. Drop check constraints that reference the enum
    if check_constraints_to_drop is not None:
        for constraint in check_constraints_to_drop:
            op.execute(f'ALTER TABLE "{table_name}" DROP CONSTRAINT IF EXISTS "{constraint}"')


    # Rename old enum type
    old_enum_temp_name = f"{enum_name}_old"
    op.execute(f'ALTER TYPE "{enum_name}" RENAME TO "{old_enum_temp_name}"')

    # Create new enum type with the updated values
    new_enum_type = sa.Enum(*new_enum_values, name=enum_name)
    new_enum_type.create(op.get_bind())

    # Alter the column type to use the new enum type
    if conversion_mappings is None:
        op.execute(f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" TYPE "{enum_name}" USING "{column_name}"::text::{enum_name}')
    if conversion_mappings is not None:
        case_when: str = ""
        for old_value, new_value in conversion_mappings.items():
            case_when += f"WHEN '{old_value}' THEN '{new_value}'\n"

        op.execute(f"""
            ALTER TABLE "{table_name}"
            ALTER COLUMN "{column_name}" TYPE "{enum_name}" 
            USING CASE {column_name}::text
            {case_when}
            ELSE "{column_name}"::text
            END::{enum_name};
        """)

    # Drop the old enum type
    if drop_old_enum:
        op.execute(f'DROP TYPE "{old_enum_temp_name}"')

def alter_enum_value(
        enum_name,
        old_value,
        new_value
):
    """
    Changes one value of an enum type
    """
    op.execute(f"ALTER TYPE {enum_name} RENAME VALUE '{old_value}' TO '{new_value}'")

def id_column() -> sa.Column:
    """Returns a standard `id` column."""
    return sa.Column(
        'id',
        sa.Integer(),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment='The primary identifier for the row.'
    )

def created_at_column() -> sa.Column:
    """Returns a standard `created_at` column."""
    return sa.Column(
        'created_at',
        sa.DateTime(),
        server_default=sa.text('now()'),
        nullable=False,
        comment='The time the row was created.'
    )

def updated_at_column() -> sa.Column:
    """Returns a standard `updated_at` column."""
    return sa.Column(
        'updated_at',
        sa.DateTime(),
        server_default=sa.text('now()'),
        server_onupdate=sa.text('now()'),
        nullable=False,
        comment='The last time the row was updated.'
    )

def task_id_column() -> sa.Column:
    return sa.Column(
        'task_id',
        sa.Integer(),
        sa.ForeignKey(
            'tasks.id',
            ondelete='CASCADE'
        ),
        nullable=False,
        comment='A foreign key to the `tasks` table.'
    )

def url_id_column(name: str = 'url_id', primary_key: bool = False) -> sa.Column:
    return sa.Column(
        name,
        sa.Integer(),
        sa.ForeignKey(
            'urls.id',
            ondelete='CASCADE'
        ),
        primary_key=primary_key,
        nullable=False,
        comment='A foreign key to the `urls` table.'
    )

def user_id_column(name: str = 'user_id') -> sa.Column:
    return sa.Column(
        name,
        sa.Integer(),
        nullable=False,
    )


def location_id_column(name: str = 'location_id') -> sa.Column:
    return sa.Column(
        name,
        sa.Integer(),
        sa.ForeignKey(
            'locations.id',
            ondelete='CASCADE'
        ),
        nullable=False,
        comment='A foreign key to the `locations` table.'
    )

def batch_id_column(nullable=False) -> sa.Column:
    return sa.Column(
        'batch_id',
        sa.Integer(),
        sa.ForeignKey(
            'batches.id',
            ondelete='CASCADE'
        ),
        nullable=nullable,
        comment='A foreign key to the `batches` table.'
    )

def agency_id_column(nullable=False) -> sa.Column:
    return sa.Column(
        'agency_id',
        sa.Integer(),
        sa.ForeignKey(
            'agencies.agency_id',
            ondelete='CASCADE'
        ),
        nullable=nullable,
        comment='A foreign key to the `agencies` table.'
    )

def add_enum_value(
    enum_name: str,
    enum_value: str
) -> None:
    op.execute(f"ALTER TYPE {enum_name} ADD VALUE '{enum_value}'")