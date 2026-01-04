from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.base import Base


class URLInternetArchivesProbeMetadata(
    Base,
    URLDependentMixin
):
    __tablename__ = 'url_internet_archives_probe_metadata'
    __table_args__ = (
        PrimaryKeyConstraint("url_id"),
    )

    archive_url: Mapped[str]
    digest: Mapped[str]
    length: Mapped[int]