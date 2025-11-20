import pytest

from src.api.endpoints.check.unique_url.response import CheckUniqueURLResponse
from tests.automated.integration.readonly.helper import ReadOnlyTestHelper
from tests.helpers.api_test_helper import APITestHelper


@pytest.mark.asyncio
async def test_check_unique_url(
    readonly_helper: ReadOnlyTestHelper
):

    ath: APITestHelper = readonly_helper.api_test_helper
    response_not_unique_url = ath.request_validator.get_v3(
        url="/check/unique-url",
        params={
            "url": "https://read-only-ds.com"
        }
    )
    model_not_unique_url = CheckUniqueURLResponse(**response_not_unique_url)
    assert not model_not_unique_url.unique_url
    assert model_not_unique_url.url_id == readonly_helper.maximal_data_source_url_id


    response_unique_url = ath.request_validator.get_v3(
        url="/check/unique-url",
        params={
            "url": "https://nonexistent-url.com"
        }
    )
    model_unique_url = CheckUniqueURLResponse(**response_unique_url)
    assert model_unique_url.unique_url
    assert model_unique_url.url_id is None