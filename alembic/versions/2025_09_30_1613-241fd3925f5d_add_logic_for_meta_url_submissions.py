"""Add logic for meta URL submissions

Revision ID: 241fd3925f5d
Revises: 84a3de626ad8
Create Date: 2025-09-30 16:13:03.980113

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import url_id_column, created_at_column

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
        sa.Column("ds_meta_url_id", sa.Integer(), nullable=False),
        created_at_column(),
        sa.PrimaryKeyConstraint(
            "url_id",
        ),
        sa.UniqueConstraint(
            "ds_meta_url_id"
        )
    )


def downgrade() -> None:
    pass
