import pytest

from tests.automated.integration.readonly.helper import ReadOnlyTestHelper
from tests.helpers.check import check_forbidden_url_type


@pytest.mark.asyncio
async def test_forbid(readonly_helper: ReadOnlyTestHelper):
    check_forbidden_url_type(
        route=f"/data-sources/{readonly_helper.url_meta_url_id}/agencies",
        api_test_helper=readonly_helper.api_test_helper,
        method="GET"
    )
