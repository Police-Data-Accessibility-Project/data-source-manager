"""Add url scheme column

Revision ID: a8f36f185694
Revises: 7aace6587d1a
Create Date: 2025-10-14 11:05:28.686940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8f36f185694'
down_revision: Union[str, None] = '7aace6587d1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _populate_column():
    op.execute(
        """
        UPDATE urls
        SET scheme = lower(split_part(url, '://', 1))
        WHERE url ~* '^[a-z][a-z0-9+.-]*://';
        """
    )


def _remove_schemes_from_url_column():
    op.execute(
        """
        UPDATE urls
        SET url = regexp_replace(url, '^(?i)[a-z][a-z0-9+.-]*://', '')
        WHERE url ~* '^[a-z][a-z0-9+.-]*://';
        """
    )


def _add_check_constraint_to_url_column():
    op.execute(
        """
        ALTER TABLE urls
        ADD CONSTRAINT check_url_does_not_have_schema CHECK (url !~* '^[a-z][a-z0-9+.-]*://');
        """
    )


def upgrade() -> None:
    _add_column()
    _populate_column()
    _remove_schemes_from_url_column()
    _add_check_constraint_to_url_column()

def _add_column():
    op.add_column(
        "urls",
        sa.Column("scheme", sa.String(), nullable=True)
    )

def downgrade() -> None:
    pass
