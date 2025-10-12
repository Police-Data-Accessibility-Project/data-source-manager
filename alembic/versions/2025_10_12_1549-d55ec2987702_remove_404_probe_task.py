"""Remove 404 Probe Task

Revision ID: d55ec2987702
Revises: 8b2adc95c5d7
Create Date: 2025-10-12 15:49:01.945412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import remove_enum_value, add_enum_value

# revision identifiers, used by Alembic.
revision: str = 'd55ec2987702'
down_revision: Union[str, None] = '8b2adc95c5d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _drop_views()
    add_enum_value(
        enum_name="url_type",
        enum_value="broken page"
    )

    op.execute(
        """DELETE FROM TASKS WHERE task_type = '404 Probe'"""
    )
    op.execute(
        """DELETE FROM url_task_error WHERE task_type = '404 Probe'"""
    )
    remove_enum_value(
        enum_name="task_type",
        value_to_remove="404 Probe",
        targets=[
            ("tasks", "task_type"),
            ("url_task_error", "task_type")
        ]
    )
    op.execute(
        """UPDATE URLS SET status = 'ok' WHERE status = '404 not found'"""
    )
    remove_enum_value(
        enum_name="url_status",
        value_to_remove="404 not found",
        targets=[
            ("urls", "status")
        ]
    )

    op.drop_table("url_probed_for_404")

    _recreate_views()

def _drop_views():
    op.execute("drop view url_task_count_1_day")
    op.execute("drop view url_task_count_1_week")

def _recreate_views():
    op.execute("""
    create view url_task_count_1_day(task_type, count) as
    SELECT
        t.task_type,
        count(ltu.url_id) AS count
    FROM
        tasks t
        JOIN link_task_urls ltu
             ON ltu.task_id = t.id
    WHERE
        t.updated_at > (now() - '1 day'::interval)
    GROUP BY
        t.task_type;
    """)

    op.execute("""
    create view url_task_count_1_week(task_type, count) as
    SELECT
        t.task_type,
        count(ltu.url_id) AS count
    FROM
        tasks t
        JOIN link_task_urls ltu
             ON ltu.task_id = t.id
    WHERE
        t.updated_at > (now() - '7 days'::interval)
    GROUP BY
        t.task_type;    
    """)

def downgrade() -> None:
    pass
