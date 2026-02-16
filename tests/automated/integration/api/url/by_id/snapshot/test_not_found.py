import pytest
from fastapi import Response

from tests.helpers.api_test_helper import APITestHelper


@pytest.mark.asyncio
async def test_get_url_screenshot_not_found(api_test_helper: APITestHelper):

    response: Response = await api_test_helper.request_validator.get_url_screenshot(url_id=1)
    assert response.status_code == 404