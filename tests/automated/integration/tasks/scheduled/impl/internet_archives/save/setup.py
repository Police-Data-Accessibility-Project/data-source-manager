from datetime import datetime, timedelta

from sqlalchemy import update

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.checked_for_ia.pydantic import FlagURLCheckedForInternetArchivesPydantic
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from src.db.models.impl.url.internet_archives.probe.pydantic import URLInternetArchiveMetadataPydantic
from src.db.models.impl.url.internet_archives.save.pydantic import URLInternetArchiveSaveMetadataPydantic
from src.db.models.impl.url.internet_archives.save.sqlalchemy import URLInternetArchivesSaveMetadata
from src.db.models.impl.url.web_metadata.insert import URLWebMetadataPydantic
from tests.automated.integration.tasks.scheduled.impl.internet_archives.save.constants import TEST_URL_1, TEST_URL_2


async def setup_valid_entries(adb_client: AsyncDatabaseClient) -> list[int]:

    # Add 2 URLs
    url_ids = await add_test_urls(adb_client)

    # Add IA Probe Metadata and Flag to each
    await add_ia_probe_info(adb_client, url_ids)

    # Add URL Probe Metadata to each
    await add_url_probe_metadata(adb_client, url_ids)

    return url_ids


async def add_url_probe_metadata(
    adb_client: AsyncDatabaseClient,
    url_ids: list[int],
    status_code: int = 200
) -> None:
    url_probe_metadata_inserts: list[URLWebMetadataPydantic] = []
    for url_id in url_ids:
        url_probe_metadata_inserts.append(
            URLWebMetadataPydantic(
                url_id=url_id,
                accessed=True,
                status_code=status_code,
                content_type="text/html",
                error_message=None
            )
        )
    await adb_client.bulk_insert(url_probe_metadata_inserts)


async def add_ia_probe_info(adb_client: AsyncDatabaseClient, url_ids: list[int]) -> None:
    ia_probe_metadata_inserts: list[URLInternetArchiveMetadataPydantic] = []
    ia_probe_flag_inserts: list[FlagURLCheckedForInternetArchivesPydantic] = []
    for url_id in url_ids:
        ia_probe_metadata_inserts.append(
            URLInternetArchiveMetadataPydantic(
                url_id=url_id,
                archive_url="https://ia-metadata.com",
                digest="digest",
                length=1000
            )
        )
        ia_probe_flag_inserts.append(
            FlagURLCheckedForInternetArchivesPydantic(
                url_id=url_id,
                success=True
            )
        )
    await adb_client.bulk_insert(ia_probe_metadata_inserts)
    await adb_client.bulk_insert(ia_probe_flag_inserts)


async def add_test_urls(adb_client: AsyncDatabaseClient) -> list[int]:
    url_inserts: list[URLInsertModel] = [
        URLInsertModel(
            url=TEST_URL_1,
            source=URLSource.COLLECTOR,
            trailing_slash=False
        ),
        URLInsertModel(
            url=TEST_URL_2,
            source=URLSource.COLLECTOR,
            trailing_slash=False
        )
    ]
    url_ids = await adb_client.bulk_insert(url_inserts, return_ids=True)
    return url_ids


async def update_ia_save_info_to_month_old(adb_client):
    await adb_client.execute(
        update(URLInternetArchivesSaveMetadata)
        .values(last_uploaded_at=datetime.now() - timedelta(days=32))
    )


async def add_ia_save_info(adb_client, url_ids):
    ia_save_metadata_inserts: list[URLInternetArchiveSaveMetadataPydantic] = []
    for url_id in url_ids:
        ia_save_metadata_inserts.append(URLInternetArchiveSaveMetadataPydantic(url_id=url_id))
    await adb_client.bulk_insert(ia_save_metadata_inserts)
