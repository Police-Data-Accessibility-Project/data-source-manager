"""Merge url_health head with dev head

Revision ID: a1b2c3d4e5f6
Revises: f831e447b1cb, 7a6c2e1b9d44
Create Date: 2026-03-18 14:00:00.000000

"""
from typing import Optional, Sequence


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Optional[tuple[str, ...]] = ('f831e447b1cb', '7a6c2e1b9d44')
branch_labels: Optional[str | Sequence[str]] = None
depends_on: Optional[str | Sequence[str]] = None


def upgrade() -> None:
    """Merge multiple heads."""
    pass


def downgrade() -> None:
    """Downgrade merge."""
    pass
