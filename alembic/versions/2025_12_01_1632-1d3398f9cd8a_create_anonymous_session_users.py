"""Create anonymous_session_users

Revision ID: 1d3398f9cd8a
Revises: 5d6412540aba
Create Date: 2025-12-01 16:32:27.842175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '1d3398f9cd8a'
down_revision: Union[str, None] = '5d6412540aba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create anonymous_sessions table
    op.create_table(
        "anonymous_sessions",
        sa.Column(
            "id",
            UUID,
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True
        ),
    )

    # TODO: Update anonymous tables to link to anonymous sessions table

    ## TODO: Drop any unique IDs forbidding more than a single ID for these columns


def downgrade() -> None:
    pass
