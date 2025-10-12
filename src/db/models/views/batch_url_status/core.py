"""
CREATE MATERIALIZED VIEW batch_url_status_mat_view as (
    with
    batches_with_urls as (
        select
            b.id as batch_id
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
    b.id,
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
"""
from sqlalchemy import PrimaryKeyConstraint, String, Column

from src.db.models.mixins import ViewMixin, BatchDependentMixin
from src.db.models.templates_.base import Base


class BatchURLStatusMatView(
    Base,
    ViewMixin,
    BatchDependentMixin
):

    batch_url_status = Column(String)

    __tablename__ = "batch_url_status_mat_view"
    __table_args__ = (
        PrimaryKeyConstraint("batch_id"),
        {"info": "view"}
    )