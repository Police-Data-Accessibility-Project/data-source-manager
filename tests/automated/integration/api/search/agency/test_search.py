import pytest

from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo


@pytest.mark.asyncio
async def test_search_agency(
    api_test_helper: APITestHelper,
    db_data_creator: DBDataCreator,
    pittsburgh_locality: LocalityCreationInfo,
    allegheny_county: CountyCreationInfo
):

    agency_a_id: int = await db_data_creator.agency("A Agency")
    agency_b_id: int = await db_data_creator.agency("AB Agency")
    agency_c_id: int = await db_data_creator.agency("ABC Agency")

    await db_data_creator.link_agencies_to_location(
        agency_ids=[agency_a_id, agency_c_id],
        location_id=pittsburgh_locality.location_id
    )
    await db_data_creator.link_agencies_to_location(
        agency_ids=[agency_b_id],
        location_id=allegheny_county.location_id
    )

    responses: list[dict] = api_test_helper.request_validator.get_v2(
        url="/search/agency",
        params={
            "query": "A Agency",
        }
    )
    assert len(responses) == 3
    assert responses[0]["agency_id"] == agency_a_id
    assert responses[1]["agency_id"] == agency_b_id
    assert responses[2]["agency_id"] == agency_c_id

    # Filter based on location ID
    responses = api_test_helper.request_validator.get_v2(
        url="/search/agency",
        params={
            "query": "A Agency",
            "location_id": pittsburgh_locality.location_id
        }
    )

    assert len(responses) == 2
    assert responses[0]["agency_id"] == agency_a_id
    assert responses[1]["agency_id"] == agency_c_id

    # Filter again based on location ID but with Allegheny County
    # Confirm pittsburgh agencies are picked up
    responses = api_test_helper.request_validator.get_v2(
        url="/search/agency",
        params={
            "query": "A Agency",
            "location_id": allegheny_county.location_id
        }
    )
    assert len(responses) == 3
