from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, URLDependentMixin, LastSyncedAtMixin
from src.db.models.templates_.with_id import WithIDBase


class DSAppLinkDataSource(
    CreatedAtMixin,
    URLDependentMixin,
    WithIDBase,
    LastSyncedAtMixin
):
    __tablename__ = "ds_app_link_data_source"

    url_id = Column(
        Integer,
        ForeignKey(
            'urls.id',
            ondelete="SET NULL",
        ),
        nullable=True
    )
    ds_data_source_id = Column(Integer, nullable=False, primary_key=True)

    # Relationships
    url = relationship(
        "URL",
        back_populates="data_source",
        uselist=False
    )
