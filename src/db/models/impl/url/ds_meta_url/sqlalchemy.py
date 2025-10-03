from sqlalchemy import Column, Integer, PrimaryKeyConstraint, UniqueConstraint

from src.db.models.mixins import URLDependentMixin, CreatedAtMixin, AgencyDependentMixin
from src.db.models.templates_.base import Base


class URLDSMetaURL(
    Base,
    URLDependentMixin,
    AgencyDependentMixin,
    CreatedAtMixin
):
    __tablename__ = "url_ds_meta_url"

    ds_meta_url_id = Column(Integer)

    __table_args__ = (
        PrimaryKeyConstraint("url_id", "agency_id"),
        UniqueConstraint("ds_meta_url_id"),
    )