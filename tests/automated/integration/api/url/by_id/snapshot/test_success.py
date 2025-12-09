import pytest

from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.models.impl.url.screenshot.sqlalchemy import URLScreenshot
from tests.automated.integration.api._helpers.RequestValidator import RequestValidator
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_get_url_screenshot_success(
    api_test_helper: APITestHelper
):
    ath: APITestHelper = api_test_helper
    ddc: DBDataCreator = api_test_helper.db_data_creator
    rv: RequestValidator = ath.request_validator

    url_mapping: SimpleURLMapping = (await ddc.create_urls())[0]
    url_id: int = url_mapping.url_id

    url_screenshot = URLScreenshot(
        url_id=url_id,
        content=b"test",
        file_size=4
    )
    await ddc.adb_client.add(url_screenshot)

    response = await rv.get_url_screenshot(url_id=url_id)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/webp"
    assert response.content == b"test"
    assert response.headers["Content-Length"] == "4"
