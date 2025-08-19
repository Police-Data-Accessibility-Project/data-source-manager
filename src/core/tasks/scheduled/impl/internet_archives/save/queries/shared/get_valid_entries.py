from sqlalchemy import select, or_, func, text

from src.db.models.impl.flag.checked_for_ia.sqlalchemy import FlagURLCheckedForInternetArchives
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.internet_archives.probe.sqlalchemy import URLInternetArchivesProbeMetadata
from src.db.models.impl.url.internet_archives.save.sqlalchemy import URLInternetArchivesSaveMetadata
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata

IA_SAVE_VALID_ENTRIES_QUERY = (
    select(
        URL.id,
        URL.url,
        (URLInternetArchivesSaveMetadata.url_id.is_(None)).label("is_new"),
    )
    # URL must have been previously probed for its online status.
    .join(
        URLWebMetadata,
        URL.id == URLWebMetadata.url_id
    )
    # URL must have been previously probed for an Internet Archive URL.
    .join(
        FlagURLCheckedForInternetArchives,
        URL.id == FlagURLCheckedForInternetArchives.url_id
    )

    .outerjoin(
        URLInternetArchivesProbeMetadata,
        URL.id == URLInternetArchivesProbeMetadata.url_id
    )
    .outerjoin(
        URLInternetArchivesSaveMetadata,
        URL.id == URLInternetArchivesSaveMetadata.url_id,

    )
    .where(
        # Must not have been archived at all
        # OR not have been archived in the last month
        or_(
            URLInternetArchivesSaveMetadata.url_id.is_(None),
            URLInternetArchivesSaveMetadata.last_uploaded_at < func.now() - text("INTERVAL '1 month'")
        ),
        # Must have returned a 200 status code
        URLWebMetadata.status_code == 200
    )
    # Order favoring URLs that have never been archived, and never been probed
    .order_by(
        URLInternetArchivesProbeMetadata.url_id.is_(None).desc(),
        URLInternetArchivesSaveMetadata.url_id.is_(None).desc(),
    )
    .limit(100)
)