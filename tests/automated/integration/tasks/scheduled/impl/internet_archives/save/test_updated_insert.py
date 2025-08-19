from datetime import datetime
from unittest.mock import create_autospec

import pytest

from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.internet_archives.save.operator import InternetArchivesSaveTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.internet_archives.save.sqlalchemy import URLInternetArchivesSaveMetadata
from src.external.internet_archives.models.save_response import InternetArchivesSaveResponseInfo
from tests.automated.integration.tasks.scheduled.impl.internet_archives.save.constants import TEST_URL_2, TEST_URL_1
from tests.automated.integration.tasks.scheduled.impl.internet_archives.save.setup import setup_valid_entries, \
    add_ia_save_info, update_ia_save_info_to_month_old
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error


@pytest.mark.asyncio
async def test_updated_insert(operator: InternetArchivesSaveTaskOperator):
    adb_client: AsyncDatabaseClient = operator.adb_client

    # Get current system date time
    current_date_time: datetime = await adb_client.get_current_database_time()

    url_ids: list[int] = await setup_valid_entries(operator.adb_client)


    # Add old IA Save Metadata, set to be over a month old
    await add_ia_save_info(adb_client, url_ids=url_ids)
    await update_ia_save_info_to_month_old(adb_client)

    # Set up IA Client to return successful response
    mock_save = create_autospec(
        operator.ia_client.save_to_internet_archives
    )
    operator.ia_client.save_to_internet_archives = mock_save
    mock_save.side_effect = [
        InternetArchivesSaveResponseInfo(
            url=TEST_URL_1,
            error=None
        ),
        InternetArchivesSaveResponseInfo(
            url=TEST_URL_2,
            error=None
        )
    ]

    # Confirm task prerequisites are met
    await operator.meets_task_prerequisites()

    # Run task
    run_info: TaskOperatorRunInfo = await operator.run_task()

    # Confirm task ran without error
    assert_task_ran_without_error(run_info)

    # Confirm task prerequisites no longer met
    assert not await operator.meets_task_prerequisites()

    # Confirm IA Save Metadata was updated
    metadata_list: list[URLInternetArchivesSaveMetadata] = await operator.adb_client.get_all(
        URLInternetArchivesSaveMetadata
    )
    assert len(metadata_list) == 2

    for metadata in metadata_list:
        assert metadata.url_id in url_ids
        assert metadata.last_uploaded_at > current_date_time.replace(tzinfo=None)



