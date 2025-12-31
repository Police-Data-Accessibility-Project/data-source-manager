import pytest

from src.core.tasks.url.operators.html.core import URLHTMLTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from tests.automated.integration.tasks.url.impl.asserts import assert_prereqs_not_met, assert_task_ran_without_error
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_non_200(
    adb_client_test: AsyncDatabaseClient,
    db_data_creator: DBDataCreator,
    operator: URLHTMLTaskOperator,
    test_url_id: int
):
    """
    URLs with non-200 web metadata should not be processed
    """
    await db_data_creator.create_web_metadata(
        url_ids=[test_url_id],
        status_code=500
    )

    await assert_prereqs_not_met(operator)

    run_info = await operator.run_task()
    assert_task_ran_without_error(run_info)

    # Check for the absence of Compressed HTML Data
    results: list[URLCompressedHTML] = await adb_client_test.get_all(URLCompressedHTML)
    assert len(results) == 0