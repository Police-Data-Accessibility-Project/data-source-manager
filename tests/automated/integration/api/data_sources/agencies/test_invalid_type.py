import pytest

from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.check import check_forbidden_url_type


@pytest.mark.asyncio
async def test_invalid_type(
    api_test_helper: APITestHelper,
    test_url_meta_url_id: int,
    test_agency_id: int
):
    for method in ['POST', 'DELETE']:
        check_forbidden_url_type(
            method=method,
            route=f"/data-sources/{test_url_meta_url_id}/agencies/{test_agency_id}",
            api_test_helper=api_test_helper,
        )