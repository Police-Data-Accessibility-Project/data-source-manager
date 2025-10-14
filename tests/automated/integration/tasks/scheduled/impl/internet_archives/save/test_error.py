from unittest.mock import create_autospec

import pytest

from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.internet_archives.save.operator import InternetArchivesSaveTaskOperator
from src.db.models.impl.url.task_error.sqlalchemy import URLTaskError
from tests.automated.integration.tasks.scheduled.impl.internet_archives.save.setup import setup_valid_entries
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error


@pytest.mark.asyncio
async def test_error(operator: InternetArchivesSaveTaskOperator):

    url_ids: list[int] = await setup_valid_entries(operator.adb_client)

    # Set up IA client to raise error
    mock_save = create_autospec(
        operator.ia_client._save_url
    )
    operator.ia_client._save_url = mock_save
    mock_save.side_effect = [
        ValueError("This is a test error"),
        RuntimeError("This is another test error")
    ]


    # Confirm task prerequisites are met
    await operator.meets_task_prerequisites()

    # Run task
    run_info: TaskOperatorRunInfo = await operator.run_task()

    # Confirm task pre-requisites are still met
    await operator.meets_task_prerequisites()

    # Confirm task ran without error
    assert_task_ran_without_error(run_info)

    # Confirm URL Error info was added
    url_error_list: list[URLTaskError] = await operator.adb_client.get_all(URLTaskError)
    assert len(url_error_list) == 2
    assert {url_error.url_id for url_error in url_error_list} == set(url_ids)
    assert {url_error.error for url_error in url_error_list} == {
        "ValueError: This is a test error",
        "RuntimeError: This is another test error"
    }
