import pytest

from src.api.endpoints.data_source.by_id.put.request import DataSourcePutRequest
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.check import check_forbidden_url_type


@pytest.mark.asyncio
async def test_invalid_type(
    api_test_helper: APITestHelper,
    test_url_meta_url_id: int
):
    check_forbidden_url_type(
        method="PUT",
        route=f"/data-sources/{test_url_meta_url_id}",
        api_test_helper=api_test_helper,
        json=DataSourcePutRequest(
            name="test"
        ).model_dump(mode='json')
    )