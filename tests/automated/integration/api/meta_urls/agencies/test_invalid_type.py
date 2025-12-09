import pytest

from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.check import check_forbidden_url_type


@pytest.mark.asyncio
async def test_invalid_type(
    api_test_helper: APITestHelper,
    test_url_data_source_id: int,
    test_agency_id: int
):
    for method in ['POST', 'DELETE']:
        check_forbidden_url_type(
            method=method,
            route=f"/meta-urls/{test_url_data_source_id}/agencies/{test_agency_id}",
            api_test_helper=api_test_helper,
        )