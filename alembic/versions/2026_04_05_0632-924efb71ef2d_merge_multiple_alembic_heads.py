"""Merge multiple Alembic heads

Revision ID: 924efb71ef2d
Revises: c4f9bbf8a201, a1b2c3d4e5f6
Create Date: 2026-04-05 06:32:10.302444

"""
from typing import Optional, Sequence, Union


# revision identifiers, used by Alembic.
revision: str = '924efb71ef2d'
down_revision: Optional[str] = ('c4f9bbf8a201', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge heads."""


def downgrade() -> None:
    """Merge heads."""
