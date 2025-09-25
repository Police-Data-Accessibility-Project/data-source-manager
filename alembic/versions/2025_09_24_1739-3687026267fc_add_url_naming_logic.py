"""Add URL naming logic

Revision ID: 3687026267fc
Revises: e6a1a1b3bad4
Create Date: 2025-09-24 17:39:55.353947

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import id_column, url_id_column, created_at_column, user_id_column

# revision identifiers, used by Alembic.
revision: str = '3687026267fc'
down_revision: Union[str, None] = 'e6a1a1b3bad4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    _add_auto_name_task()
    _create_url_name_suggestion_table()
    _create_link_user_name_suggestion_table()

def _add_auto_name_task():
    op.execute("""ALTER TYPE task_type ADD VALUE 'Auto Name';""")


def _create_url_name_suggestion_table():
    op.create_table(
        'url_name_suggestions',
        id_column(),
        url_id_column(),
        sa.Column('suggestion', sa.String(
            length=100
        ), nullable=False),
        sa.Column(
            'source', sa.Enum(
                "HTML Metadata Title",
                "User",
                name="suggestion_source_enum"
            )
        ),
        created_at_column(),
        sa.UniqueConstraint(
            'url_id', 'suggestion', name='url_name_suggestions_url_id_source_unique'
        )
    )


def _create_link_user_name_suggestion_table():
    op.create_table(
        'link_user_name_suggestions',
        user_id_column(),
        sa.Column(
            "suggestion_id",
            sa.Integer(),
            sa.ForeignKey("url_name_suggestions.id"),
            nullable=False,
        ),
        created_at_column(),
        sa.PrimaryKeyConstraint(
            "user_id",
            "suggestion_id"
        )
    )