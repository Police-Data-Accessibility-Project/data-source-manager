"""Add logic for meta URL submissions

Revision ID: 241fd3925f5d
Revises: 84a3de626ad8
Create Date: 2025-09-30 16:13:03.980113

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from src.util.alembic_helpers import url_id_column, created_at_column, agency_id_column

# revision identifiers, used by Alembic.
revision: str = '241fd3925f5d'
down_revision: Union[str, None] = '84a3de626ad8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""ALTER TYPE task_type ADD VALUE 'Submit Meta URLs'""")
    op.create_table(
        "url_ds_meta_url",
        url_id_column(),
        agency_id_column(),
        sa.Column("ds_meta_url_id", sa.Integer(), nullable=False),
        created_at_column(),
        sa.PrimaryKeyConstraint(
            "url_id",
            "agency_id"
        ),
        sa.UniqueConstraint(
            "ds_meta_url_id"
        )
    )
    op.execute("""ALTER TYPE task_type ADD VALUE 'Delete Stale Screenshots'""")
    op.execute("""ALTER TYPE task_type ADD VALUE 'Mark Task Never Completed'""")
    op.execute("""
        CREATE TYPE task_status_enum as ENUM(
            'complete',
            'in-process',
            'error',
            'aborted',
            'never-completed'
        )
    """)
    op.execute("""
            ALTER TABLE tasks
              ALTER COLUMN status DROP DEFAULT,
              ALTER COLUMN status TYPE task_status_enum
              USING (
                CASE status::text                               -- old enum -> text
                  WHEN 'ready to label'  THEN 'complete'::task_status_enum
                  ELSE status::text::task_status_enum
                END
              );
    """)


def downgrade() -> None:
    pass
