"""Remove 404 Probe Task

Revision ID: d55ec2987702
Revises: 25b3fc777c31
Create Date: 2025-10-12 15:49:01.945412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import remove_enum_value, add_enum_value

# revision identifiers, used by Alembic.
revision: str = 'd55ec2987702'
down_revision: Union[str, None] = '25b3fc777c31'
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
    op.execute("drop materialized view url_status_mat_view")

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

    op.execute(
        """
    CREATE MATERIALIZED VIEW url_status_mat_view AS
    with
    urls_with_relevant_errors as (
        select
            ute.url_id
        from
            url_task_error ute
        where
            ute.task_type in (
                              'Screenshot',
                              'HTML',
                              'URL Probe'
                )
        )
    select
        u.id as url_id,
        case
            when (
                -- Validated as not relevant, individual record, or not found
                fuv.type in ('not relevant', 'individual record', 'not found')
                    -- Has Meta URL in data sources app
                    OR udmu.url_id is not null
                    -- Has data source in data sources app
                    OR uds.url_id is not null
                ) Then 'Submitted/Pipeline Complete'
            when fuv.type is not null THEN 'Accepted'
            when (
                -- Has compressed HTML
                uch.url_id is not null
                    AND
                    -- Has web metadata
                uwm.url_id is not null
                    AND
                    -- Has screenshot
                us.url_id is not null
                ) THEN 'Community Labeling'
            when uwre.url_id is not null then 'Error'
            ELSE 'Intake'
            END as status

    from
        urls u
        left join urls_with_relevant_errors uwre
                  on u.id = uwre.url_id
        left join url_screenshot us
                  on u.id = us.url_id
        left join url_compressed_html uch
                  on u.id = uch.url_id
        left join url_web_metadata uwm
                  on u.id = uwm.url_id
        left join flag_url_validated fuv
                  on u.id = fuv.url_id
        left join url_ds_meta_url udmu
                  on u.id = udmu.url_id
        left join url_data_source uds
                  on u.id = uds.url_id
    """
        )


def downgrade() -> None:
    pass
