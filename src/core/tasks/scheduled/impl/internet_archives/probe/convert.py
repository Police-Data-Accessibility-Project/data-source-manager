from src.db.models.impl.url.internet_archives.probe.pydantic import URLInternetArchiveMetadataPydantic
from src.external.internet_archives.models.ia_url_mapping import InternetArchivesURLMapping
from src.util.url_mapper import URLMapper


def convert_ia_url_mapping_to_ia_metadata(
    url_mapper: URLMapper,
    ia_mapping: InternetArchivesURLMapping
) -> URLInternetArchiveMetadataPydantic:
    iam = ia_mapping.ia_metadata
    return URLInternetArchiveMetadataPydantic(
        url_id=url_mapper.get_id(ia_mapping.url),
        archive_url=iam.archive_url,
        digest=iam.digest,
        length=iam.length
    )
