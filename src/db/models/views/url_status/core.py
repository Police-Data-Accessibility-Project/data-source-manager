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
from sqlalchemy import String, Column

from src.db.models.helpers import url_id_primary_key_constraint
from src.db.models.mixins import ViewMixin, URLDependentMixin, URLDependentViewMixin
from src.db.models.templates_.base import Base


class URLStatusMatView(
    Base,
    URLDependentViewMixin
):
    __tablename__ = "url_status_mat_view"

    status = Column(String)