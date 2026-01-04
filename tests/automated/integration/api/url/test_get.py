import pytest

from src.api.endpoints.url.get.dto import GetURLsResponseInfo
from src.db.dtos.url.insert import InsertURLsInfo
from tests.helpers.api_test_helper import APITestHelper


@pytest.mark.asyncio
async def test_get_urls(api_test_helper: APITestHelper):
    # Basic test, no results
    data: GetURLsResponseInfo = api_test_helper.request_validator.get_urls()

    assert data.urls == []
    assert data.count == 0

    db_data_creator = api_test_helper.db_data_creator

    # Create batch with status `in-process` and strategy `example`
    batch_id = db_data_creator.batch()
    # Create 2 URLs with outcome `pending`
    iui: InsertURLsInfo = db_data_creator.urls(batch_id=batch_id, url_count=3)

    url_id_1st = iui.url_mappings[0].url_id

    # Get the latter 2 urls
    url_ids = [iui.url_mappings[1].url_id, iui.url_mappings[2].url_id]

    # Add errors
    await db_data_creator.task_errors(url_ids=url_ids)

    await api_test_helper.adb_client().refresh_materialized_views()

    data: GetURLsResponseInfo = api_test_helper.request_validator.get_urls()
    assert data.count == 3
    assert len(data.urls) == 3
    assert data.urls[0].url == iui.url_mappings[0].url

    for i in range(1, 3):
        assert data.urls[i].url == iui.url_mappings[i].url
        assert len(data.urls[i].errors) == 1

    # Retrieve data again with errors only
    data: GetURLsResponseInfo = api_test_helper.request_validator.get_urls(errors=True)
    assert data.count == 2
    assert len(data.urls) == 2
    for url in data.urls:
        assert url.id != url_id_1st

