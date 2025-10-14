import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ENUM


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

def enum_column(
    column_name,
    enum_name
) -> sa.Column:
    return sa.Column(
        column_name,
        ENUM(name=enum_name, create_type=False),
        nullable=False,
        comment=f'The {column_name} of the row.'
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



def _q_ident(s: str) -> str:
    return '"' + s.replace('"', '""') + '"'


def _q_label(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def remove_enum_value(
    *,
    enum_name: str,
    value_to_remove: str,
    targets: list[tuple[str, str]],  # (table, column)
    schema: str = "public",
) -> None:
    """
    Remove `value_to_remove` from ENUM `schema.enum_name` across the given (table, column) pairs.
    Assumes target columns have **no defaults**.
    """
    conn = op.get_bind()

    # 1) Load current labels (ordered)
    labels = [
        r[0]
        for r in conn.execute(
            text(
                """
                SELECT e.enumlabel
                FROM pg_enum e
                JOIN pg_type t ON t.oid = e.enumtypid
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = :enum_name
                  AND n.nspname = :schema
                ORDER BY e.enumsortorder
                """
            ),
            {"enum_name": enum_name, "schema": schema},
        ).fetchall()
    ]
    if not labels:
        raise RuntimeError(f"Enum {schema}.{enum_name!r} not found.")
    if value_to_remove not in labels:
        return  # nothing to do
    new_labels = [l for l in labels if l != value_to_remove]
    if not new_labels:
        raise RuntimeError("Refusing to remove the last remaining enum label.")

    # Deduplicate targets while preserving order
    seen = set()
    targets = [(t, c) for (t, c) in targets if not ((t, c) in seen or seen.add((t, c)))]

    # 2) Ensure no rows still hold the label
    for table, col in targets:
        count = conn.execute(
            text(
                f"SELECT COUNT(*) FROM {_q_ident(schema)}.{_q_ident(table)} "
                f"WHERE {_q_ident(col)} = :v"
            ),
            {"v": value_to_remove},
        ).scalar()
        if count and count > 0:
            raise RuntimeError(
                f"Cannot remove {value_to_remove!r}: {schema}.{table}.{col} "
                f"has {count} row(s) with that value. UPDATE or DELETE them first."
            )

    # 3) Create a tmp enum without the value
    tmp_name = f"{enum_name}__tmp__{uuid.uuid4().hex[:8]}"
    op.execute(
        text(
            f"CREATE TYPE {_q_ident(schema)}.{_q_ident(tmp_name)} AS ENUM ("
            + ", ".join(_q_label(l) for l in new_labels)
            + ")"
        )
    )

    # 4) For each column: enum -> text -> tmp_enum
    for table, col in targets:
        op.execute(
            text(
                f"ALTER TABLE {_q_ident(schema)}.{_q_ident(table)} "
                f"ALTER COLUMN {_q_ident(col)} TYPE TEXT USING {_q_ident(col)}::TEXT"
            )
        )
        op.execute(
            text(
                f"ALTER TABLE {_q_ident(schema)}.{_q_ident(table)} "
                f"ALTER COLUMN {_q_ident(col)} TYPE {_q_ident(schema)}.{_q_ident(tmp_name)} "
                f"USING {_q_ident(col)}::{_q_ident(schema)}.{_q_ident(tmp_name)}"
            )
        )

    # 5) Swap: drop old enum, rename tmp -> original name
    op.execute(text(f"DROP TYPE {_q_ident(schema)}.{_q_ident(enum_name)}"))
    op.execute(
        text(
            f"ALTER TYPE {_q_ident(schema)}.{_q_ident(tmp_name)} "
            f"RENAME TO {_q_ident(enum_name)}"
        )
    )