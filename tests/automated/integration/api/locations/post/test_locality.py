import pytest

from src.api.endpoints.locations.post.request import AddLocationRequestModel
from src.api.endpoints.locations.post.response import AddLocationResponseModel
from src.db import Locality, Location
from src.db.client.async_ import AsyncDatabaseClient
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo


@pytest.mark.asyncio
async def test_add_locality(
    allegheny_county: CountyCreationInfo,
    adb_client_test: AsyncDatabaseClient,
    api_test_helper: APITestHelper
):
    # Add Locality
    locality_response: dict = api_test_helper.request_validator.post_v3(
        "/locations",
        json=AddLocationRequestModel(
            locality_name="Test Locality",
            county_id=allegheny_county.county_id
        ).model_dump(mode='json')
    )
    response_model = AddLocationResponseModel(
        **locality_response
    )

    # Confirm exists in database
    localities: list[Locality] = await adb_client_test.get_all(Locality)
    assert len(localities) == 1
    assert localities[0].name == "Test Locality"
    assert localities[0].county_id == allegheny_county.county_id

    locations: list[Location] = await adb_client_test.get_all(Location)
    assert len(locations) == 3
    location_ids = {location.id for location in locations}
    assert response_model.location_id in location_ids
