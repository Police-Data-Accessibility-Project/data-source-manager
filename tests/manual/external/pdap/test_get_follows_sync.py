import pytest

from src.external.pdap.impl.sync.follows.core import GetFollowsRequestBuilder


@pytest.mark.asyncio
async def test_get_follows_sync(pdap_client_dev):

    response = await pdap_client_dev.run_request_builder(
        GetFollowsRequestBuilder()
    )
    print(response)
