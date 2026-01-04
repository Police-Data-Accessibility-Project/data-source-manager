import pytest

from src.api.endpoints.meta_url.by_id.put.request import UpdateMetaURLRequest
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from tests.helpers.api_test_helper import APITestHelper


@pytest.mark.asyncio
async def test_put(
    api_test_helper: APITestHelper,
    test_url_meta_url_id: int,
    test_batch_id: int
):
    api_test_helper.request_validator.put_v3(
        url=f"/meta-urls/{test_url_meta_url_id}",
        json=UpdateMetaURLRequest(
            url="new-meta-url.com",
            name="Modified name",
            description="Modified description",
            batch_id=test_batch_id
        ).model_dump(mode='json')
    )

    adb_client: AsyncDatabaseClient = api_test_helper.adb_client()

    # Check URL updated (including schema and trailing slash)
    url: URL = (await adb_client.get_all(URL))[0]
    assert url.url == "new-meta-url.com"
    assert url.name == "Modified name"
    assert url.scheme == ""
    assert url.trailing_slash == False
    assert url.description == "Modified description"

    # Check Batch ID
    link: LinkBatchURL = (await adb_client.get_all(LinkBatchURL))[0]
    assert link.batch_id == test_batch_id

