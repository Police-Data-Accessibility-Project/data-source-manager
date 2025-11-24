"""
    create view integrity__incomplete_data_sources_view as
        select
            ds.url_id,
            fuv.url_id is not null as has_validated_flag,
            fuv.type as validated_type,
            urt.url_id is not null as has_record_type,
            lau.url_id is not null as has_agency_flag
        from ds_app_link_data_source ds
        left join flag_url_validated fuv on fuv.url_id = ds.url_id
        left join url_record_type urt on urt.url_id = ds.url_id
        left join link_agencies__urls lau on lau.url_id = ds.url_id
        where
            fuv.url_id is null
        or fuv.type != 'data source'
        or urt.url_id is null
        or lau.url_id is null
    """
from sqlalchemy import Column, Boolean

from src.db.models.helpers import enum_column
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.mixins import URLDependentViewMixin
from src.db.models.templates_.base import Base

class IntegrityIncompleteDataSource(
    Base,
    URLDependentViewMixin
):
    __tablename__ = "integrity__incomplete_data_sources_view"

    has_validated_flag = Column(Boolean)
    validated_type = enum_column(
        enum_type=URLType,
        name="url_type",
    )
    has_record_type = Column(Boolean)
    has_agency_flag = Column(Boolean)
