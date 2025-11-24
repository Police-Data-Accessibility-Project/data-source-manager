"""
    create view integrity__incomplete_data_sources_view as
    select
        mu.url_id,
        fuv.url_id is not null as has_validated_flag,
        fuv.type as validated_type
    from ds_app_link_meta_url mu
    left join flag_url_validated fuv on fuv.url_id = mu.url_id
    left join url_record_type urt on urt.url_id = mu.url_id
    where
        fuv.url_id is null
    or fuv.type != 'meta url'
    or urt.url_id is null
    """
from sqlalchemy import Column, Boolean

from src.db.models.helpers import enum_column
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.mixins import URLDependentViewMixin
from src.db.models.templates_.base import Base

class IntegrityIncompleteMetaURL(
    Base,
    URLDependentViewMixin
):
    __tablename__ = "integrity__incomplete_meta_urls_view"

    has_validated_flag = Column(Boolean)
    validated_type = enum_column(
        enum_type=URLType,
        name="url_type",
    )


