from sqlalchemy import Column, DateTime, func

from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class URLInternetArchivesSaveMetadata(
    WithIDBase,
    URLDependentMixin
):
    __tablename__ = 'url_internet_archives_save_metadata'

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    last_uploaded_at = Column(DateTime, nullable=False, server_default=func.now())
