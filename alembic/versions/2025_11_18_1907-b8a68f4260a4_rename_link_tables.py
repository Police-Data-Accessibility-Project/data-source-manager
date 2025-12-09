"""Rename link tables

Revision ID: b8a68f4260a4
Revises: 783268bd3daa
Create Date: 2025-11-18 19:07:48.518828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8a68f4260a4'
down_revision: Union[str, None] = '783268bd3daa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    old_name_new_name = {
        "link_task_urls": "link_tasks__urls",
        "link_agencies_locations": "link_agencies__locations",
        "link_agency_batches": "link_agencies__batches",
        "link_batch_urls": "link_batches__urls",
        "link_location_batches": "link_batches__locations",
        "link_urls_agency": "link_agencies__urls",
    }
    for old_name, new_name in old_name_new_name.items():
        op.rename_table(old_name, new_name)


def downgrade() -> None:
    pass
