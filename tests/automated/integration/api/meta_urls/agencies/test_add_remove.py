from src.api.endpoints.agencies.root.get.response import AgencyGetOuterResponse
from tests.helpers.api_test_helper import APITestHelper


async def test_agencies_add_remove(
    api_test_helper: APITestHelper,
    test_url_meta_url_id: int,
    test_agency_id: int
):
    api_test_helper.request_validator.post_v3(
        url=f"/meta-urls/{test_url_meta_url_id}/agencies/{test_agency_id}",
    )

    raw_response: dict = api_test_helper.request_validator.get_v3(
        url=f"/meta-urls/{test_url_meta_url_id}/agencies",
    )
    response = AgencyGetOuterResponse(**raw_response)
    assert len(response.results) == 1
    assert response.results[0].id == test_agency_id


    api_test_helper.request_validator.delete_v3(
        url=f"/meta-urls/{test_url_meta_url_id}/agencies/{test_agency_id}",
    )

    raw_response: dict = api_test_helper.request_validator.get_v3(
        url=f"/meta-urls/{test_url_meta_url_id}/agencies",
    )
    response = AgencyGetOuterResponse(**raw_response)
    assert len(response.results) == 0
