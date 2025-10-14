"""Add Batch URL Status materialized view

Revision ID: 51bde16e22f7
Revises: d55ec2987702
Create Date: 2025-10-12 18:28:28.602086

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51bde16e22f7'
down_revision: Union[str, None] = 'd55ec2987702'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE MATERIALIZED VIEW batch_url_status_mat_view as (
        with
        batches_with_urls as (
            select
                b.id
            from
                batches b
            where
                exists(
                    select
                        1
                    from
                        link_batch_urls lbu
                    where
                        lbu.batch_id = b.id
                    )
            )
        , batches_with_only_validated_urls as (
            select
                b.id
            from
                batches b
            where
                exists(
                    select
                        1
                    from
                        link_batch_urls lbu
                    left join flag_url_validated fuv on fuv.url_id = lbu.url_id
                    where
                        lbu.batch_id = b.id
                        and fuv.id is not null
                    )
                and not exists(
                    select
                        1
                    from
                        link_batch_urls lbu
                    left join flag_url_validated fuv on fuv.url_id = lbu.url_id
                    where
                        lbu.batch_id = b.id
                        and fuv.id is null
                    )
            )
    
    select
        b.id as batch_id,
        case
            when b.status = 'error' THEN 'Error'
            when (bwu.id is null) THEN 'No URLs'
            when (bwovu.id is not null) THEN 'Labeling Complete'
            else 'Has Unlabeled URLs'
        end as batch_url_status
    from
        batches b
        left join batches_with_urls bwu
                  on bwu.id = b.id
        left join batches_with_only_validated_urls bwovu
                  on bwovu.id = b.id
    )
    """)


def downgrade() -> None:
    pass
