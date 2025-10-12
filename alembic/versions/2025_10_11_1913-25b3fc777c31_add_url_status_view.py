"""Add URL status view

Revision ID: 25b3fc777c31
Revises: 8b2adc95c5d7
Create Date: 2025-10-11 19:13:03.309461

"""
from typing import Sequence, Union

from alembic import op

from src.util.alembic_helpers import add_enum_value

# revision identifiers, used by Alembic.
revision: str = '25b3fc777c31'
down_revision: Union[str, None] = '8b2adc95c5d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
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
    """)

    add_enum_value(
        enum_name="task_type",
        enum_value="Refresh Materialized Views"
    )


def downgrade() -> None:
    pass
