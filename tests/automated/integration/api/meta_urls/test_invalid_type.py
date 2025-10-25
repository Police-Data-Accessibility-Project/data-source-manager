import pytest

from src.api.endpoints.meta_url.by_id.agencies.put.request import UpdateMetaURLRequest
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.check import check_forbidden_url_type


@pytest.mark.asyncio
async def test_invalid_type(
    api_test_helper: APITestHelper,
    test_url_data_source_id: int
):
    check_forbidden_url_type(
        method="PUT",
        route=f"/meta-urls/{test_url_data_source_id}",
        api_test_helper=api_test_helper,
        json=UpdateMetaURLRequest(
            name="test"
        ).model_dump(mode='json')
    )