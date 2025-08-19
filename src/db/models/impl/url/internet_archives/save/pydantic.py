from src.db.models.impl.url.internet_archives.save.sqlalchemy import URLInternetArchivesSaveMetadata
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLInternetArchiveSaveMetadataPydantic(BulkInsertableModel):
    url_id: int

    @classmethod
    def sa_model(cls) -> type[URLInternetArchivesSaveMetadata]:
        return URLInternetArchivesSaveMetadata