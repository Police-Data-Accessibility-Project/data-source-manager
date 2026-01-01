from http import HTTPStatus

import pytest

from src.core.tasks.url.operators.html.core import URLHTMLTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.scrape_info.enums import ScrapeStatus
from src.db.models.impl.url.scrape_info.sqlalchemy import URLScrapeInfo
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from src.external.url_request.dtos.url_response import URLResponseInfo
from tests.automated.integration.tasks.url.impl.asserts import assert_prereqs_met, assert_task_ran_without_error
from tests.helpers.data_creator.core import DBDataCreator


class _MockURLRequestInterface:

    async def make_requests_with_html(self, urls: list[str]) -> list[URLResponseInfo]:
        assert len(urls) == 1
        return [
            URLResponseInfo(
                success=False,
                status=HTTPStatus.NOT_FOUND,
                exception="Not Found"
            )
        ]



@pytest.mark.asyncio
async def test_404(
    adb_client_test: AsyncDatabaseClient,
    db_data_creator: DBDataCreator,
    operator: URLHTMLTaskOperator,
    test_url_id: int
):
    """
    URLs that give 404s should be updated with the appropriate scrape status
    and their web metadata status should be updated to 404
    """
    await db_data_creator.create_web_metadata(
        url_ids=[test_url_id],
        status_code=200
    )


    # Adjust Mock Request Interface to return a 404
    operator.url_request_interface = _MockURLRequestInterface()

    await assert_prereqs_met(operator)

    run_info = await operator.run_task()
    assert_task_ran_without_error(run_info)


    # Check for the absence of Compressed HTML Data
    results: list[URLCompressedHTML] = await adb_client_test.get_all(URLCompressedHTML)
    assert len(results) == 0

    # Web Metadata should be unchanged
    web_metadata: URLWebMetadata = (await adb_client_test.get_all(URLWebMetadata))[0]
    assert web_metadata.status_code == 404

    # Check that URLScrapeInfo is updated
    scrape_info: URLScrapeInfo = (await adb_client_test.get_all(URLScrapeInfo))[0]
    assert scrape_info.status == ScrapeStatus.ERROR