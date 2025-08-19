from sqlalchemy.orm import Mapped

from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.standard import StandardBase


class URLInternetArchivesProbeMetadata(
    StandardBase,
    URLDependentMixin
):
    __tablename__ = 'url_internet_archives_probe_metadata'

    archive_url: Mapped[str]
    digest: Mapped[str]
    length: Mapped[int]