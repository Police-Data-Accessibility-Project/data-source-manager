"""
    create view integrity__url_both_data_source_and_meta_url_view as
    select
        ds.url_id
    from
        ds_app_link_data_source ds
        join ds_app_link_meta_url mu
             on mu.url_id = ds.url_id
"""

from src.db.models.mixins import URLDependentViewMixin
from src.db.models.templates_.base import Base


class IntegrityURLBothDataSourceAndMetaURL(
    Base,
    URLDependentViewMixin
):
    __tablename__ = "integrity__url_both_data_source_and_meta_url_view"


