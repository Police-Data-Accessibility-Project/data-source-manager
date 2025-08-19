from src.db.models.impl.url.internet_archives.probe.sqlalchemy import URLInternetArchivesProbeMetadata
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLInternetArchiveMetadataPydantic(BulkInsertableModel):

    url_id: int
    archive_url: str
    digest: str
    length: int

    @classmethod
    def sa_model(cls) -> type[URLInternetArchivesProbeMetadata]:
        return URLInternetArchivesProbeMetadata
