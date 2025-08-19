import pytest
from sqlalchemy import update

from src.core.tasks.scheduled.impl.internet_archives.save.operator import InternetArchivesSaveTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from tests.automated.integration.tasks.scheduled.impl.internet_archives.save.setup import add_test_urls, \
    add_ia_probe_info, add_url_probe_metadata, update_ia_save_info_to_month_old, add_ia_save_info


@pytest.mark.asyncio
async def test_prereqs(operator: InternetArchivesSaveTaskOperator):
    adb_client: AsyncDatabaseClient = operator.adb_client

    # Add just URLs
    url_ids: list[int] = await add_test_urls(adb_client)

    # Confirm operator does not yet meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add URL Probes with Flags
    await add_ia_probe_info(adb_client, url_ids=url_ids)

    # Confirm operator does not yet meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add URL Probes with non-200 status codes
    await add_url_probe_metadata(adb_client, url_ids=url_ids, status_code=404)

    # Confirm operator does not yet meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Modify URL probes to have status code 200
    await adb_client.execute(update(URLWebMetadata).values(status_code=200))

    # Confirm operator now meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Add IA Save info
    await add_ia_save_info(adb_client, url_ids)

    # Confirm operator now does not meets prerequisites
    assert not await operator.meets_task_prerequisites()

    # Modify IA Save info to be over a month old
    await update_ia_save_info_to_month_old(adb_client)

    # Confirm operator now meets prerequisites
    assert await operator.meets_task_prerequisites()






