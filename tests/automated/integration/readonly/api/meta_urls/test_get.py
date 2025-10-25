import pytest
from deepdiff import DeepDiff

from src.api.endpoints.meta_url.get.response import MetaURLGetOuterResponse, MetaURLGetResponse
from tests.automated.integration.readonly.helper import ReadOnlyTestHelper


@pytest.mark.asyncio
async def test_get(readonly_helper: ReadOnlyTestHelper):

    raw_json: dict = readonly_helper.api_test_helper.request_validator.get_v3(
        url=f"/meta-urls",
    )
    outer_response = MetaURLGetOuterResponse(**raw_json)

    assert len(outer_response.results) == 1
    response: MetaURLGetResponse = outer_response.results[0]

    diff = DeepDiff(
        response.model_dump(mode='json'),
        MetaURLGetResponse(
            url_id=readonly_helper.url_meta_url_id,
            url="read-only-meta-url.com",
            name="Read only URL Name",
            description="Read only URL",
            batch_id=None,
            agency_ids=[]
        ).model_dump(mode='json'),
    )
    assert diff == {}, f"Differences found: {diff}"