"""Update URL Status Materialized View

Revision ID: 9d57b3b79d35
Revises: 7fc6502f1fa3
Create Date: 2025-10-18 15:17:23.653448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d57b3b79d35'
down_revision: Union[str, None] = '7fc6502f1fa3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS url_status_mat_view")
    op.execute("""
    CREATE MATERIALIZED VIEW url_status_mat_view as
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
        , status_text as (
            select
                u.id as url_id,
                case
                    when (
                        -- Validated as not relevant, individual record, or not found
                        fuv.type in ('not relevant', 'individual record', 'not found')
                        ) Then 'Accepted'
                    when (
                        (fuv.type = 'data source' and uds.url_id is null)
                            OR
                        (fuv.type = 'meta url' and udmu.url_id is null)
                        ) Then 'Awaiting Submission'
                    when (
                        (fuv.type = 'data source' and uds.url_id is not null)
                            OR
                        (fuv.type = 'meta url' and udmu.url_id is not null)
                        ) Then 'Submitted'
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
        )
    select
        url_id,
        status,
        CASE status
            WHEN 'Intake' THEN 100
            WHEN 'Error' THEN 110
            WHEN 'Community Labeling' THEN 200
            WHEN 'Accepted' THEN 300
            WHEN 'Awaiting Submission' THEN 380
            WHEN 'Submitted' THEN 390
            ELSE -1
        END as code
    from status_text
    """)


def downgrade() -> None:
    pass
