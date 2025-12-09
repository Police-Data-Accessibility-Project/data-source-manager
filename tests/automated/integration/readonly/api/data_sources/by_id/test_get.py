import pytest

from src.api.endpoints.data_source.get.response import DataSourceGetResponse
from tests.automated.integration.readonly.helper import ReadOnlyTestHelper

@pytest.mark.asyncio
async def test_get_by_id(readonly_helper: ReadOnlyTestHelper):
    raw_json: dict = readonly_helper.api_test_helper.request_validator.get_v3(
        url=f"/data-sources/{readonly_helper.maximal_data_source_url_id}",
    )
    # Test response is in expected form.
    DataSourceGetResponse(**raw_json)