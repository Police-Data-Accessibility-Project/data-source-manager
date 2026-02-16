import pytest


@pytest.mark.asyncio
async def test_get_user_followed_locations(pdap_client_dev):
    response = await pdap_client_dev.get_user_followed_locations()
    print(response)