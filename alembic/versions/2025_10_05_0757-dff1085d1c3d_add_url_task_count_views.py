"""Add URL Task Count Views

Revision ID: dff1085d1c3d
Revises: f708c6a8ae5d
Create Date: 2025-10-05 07:57:09.333844

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dff1085d1c3d'
down_revision: Union[str, None] = 'f708c6a8ae5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE VIEW URL_TASK_COUNT_1_WEEK AS
    (
    select
        t.task_type,
        count(ltu.url_id)
    from
        tasks t
        join link_task_urls ltu
             on ltu.task_id = t.id
    where
        t.updated_at > (now() - INTERVAL '1 week')
    group by
        t.task_type
        )

    """)

    op.execute("""
    CREATE VIEW URL_TASK_COUNT_1_DAY AS
    (
    select
        t.task_type,
        count(ltu.url_id)
    from
        tasks t
        join link_task_urls ltu
             on ltu.task_id = t.id
    where
        t.updated_at > (now() - INTERVAL '1 day')
    group by
        t.task_type
        )

    """)


def downgrade() -> None:
    pass
