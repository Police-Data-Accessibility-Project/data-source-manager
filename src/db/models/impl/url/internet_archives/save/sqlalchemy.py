from sqlalchemy import Column, DateTime, func, PrimaryKeyConstraint

from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.base import Base


class URLInternetArchivesSaveMetadata(
    Base,
    URLDependentMixin
):
    __tablename__ = 'url_internet_archives_save_metadata'
    __table_args__ = (
        PrimaryKeyConstraint("url_id"),
    )

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    last_uploaded_at = Column(DateTime, nullable=False, server_default=func.now())
