from unittest.mock import create_autospec

import pytest

from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.internet_archives.save.operator import InternetArchivesSaveTaskOperator
from src.db.models.impl.url.internet_archives.save.sqlalchemy import URLInternetArchivesSaveMetadata
from src.external.internet_archives.models.save_response import InternetArchivesSaveResponseInfo
from tests.automated.integration.tasks.scheduled.impl.internet_archives.save.constants import TEST_URL_1, TEST_URL_2
from tests.automated.integration.tasks.scheduled.impl.internet_archives.save.setup import setup_valid_entries
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error


@pytest.mark.asyncio
async def test_new_insert(operator: InternetArchivesSaveTaskOperator):

    url_ids: list[int] = await setup_valid_entries(operator.adb_client)

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

    # Confirm IA Save Metadata was added
    metadata_list: list[URLInternetArchivesSaveMetadata] = await operator.adb_client.get_all(
        URLInternetArchivesSaveMetadata
    )
    assert len(metadata_list) == 2
    assert {metadata.url_id for metadata in metadata_list} == set(url_ids)
