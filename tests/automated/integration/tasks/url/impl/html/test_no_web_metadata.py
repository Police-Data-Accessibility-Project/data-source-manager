import pytest

from src.core.tasks.url.operators.html.core import URLHTMLTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from tests.automated.integration.tasks.url.impl.asserts import assert_prereqs_not_met, assert_task_ran_without_error


@pytest.mark.asyncio
async def test_no_web_metadata(
    adb_client_test: AsyncDatabaseClient,
    operator: URLHTMLTaskOperator,
    test_url_id: int
):
    """
    URLs with no web metadata should not be processed
    """
    await assert_prereqs_not_met(operator)

    run_info = await operator.run_task()
    assert_task_ran_without_error(run_info)

    # Check for the absence of Compressed HTML Data
    results: list[URLCompressedHTML] = await adb_client_test.get_all(URLCompressedHTML)
    assert len(results) == 0

