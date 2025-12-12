"""Create anonymous_annotation_name

Revision ID: dfb64594049f
Revises: 1d3398f9cd8a
Create Date: 2025-12-05 17:21:35.134935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from src.util.alembic_helpers import created_at_column

# revision identifiers, used by Alembic.
revision: str = 'dfb64594049f'
down_revision: Union[str, None] = '1d3398f9cd8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "link__anonymous_sessions__name_suggestions",
        sa.Column(
            "session_id",
            UUID,
            sa.ForeignKey("anonymous_sessions.id"),
            nullable=False
        ),
        sa.Column(
            "suggestion_id",
            sa.Integer(),
            sa.ForeignKey("url_name_suggestions.id"),
            nullable=False,
        ),
        created_at_column(),
        sa.PrimaryKeyConstraint(
            "session_id",
            "suggestion_id"
        )
    )


def downgrade() -> None:
    pass
