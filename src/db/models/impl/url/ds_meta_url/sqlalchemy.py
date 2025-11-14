from sqlalchemy import Column, Integer, PrimaryKeyConstraint, UniqueConstraint, ForeignKey

from src.db.models.mixins import URLDependentMixin, CreatedAtMixin, AgencyDependentMixin, LastSyncedAtMixin
from src.db.models.templates_.base import Base


class DSAppLinkMetaURL(
    Base,
    CreatedAtMixin,
    LastSyncedAtMixin
):
    __tablename__ = "ds_app_link_meta_url"

    url_id = Column(
        Integer,
        ForeignKey(
            'urls.id',
            ondelete="SET NULL",
        ),
        nullable=True
    )
    ds_meta_url_id = Column(Integer, primary_key=True)

    __table_args__ = (
        UniqueConstraint("url_id"),
    )