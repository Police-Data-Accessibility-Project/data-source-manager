import pytest

from src.api.endpoints.agencies.by_id.put.request import AgencyPutRequest
from src.api.endpoints.agencies.root.post.request import AgencyPostRequest
from src.db.models.impl.agency.enums import AgencyType, JurisdictionType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo


@pytest.mark.asyncio
async def test_agencies(
    api_test_helper: APITestHelper,
    california: USStateCreationInfo,
    pennsylvania: USStateCreationInfo
):
    ath = api_test_helper
    rv = ath.request_validator

    rv.post_v3(
        url=f"/agencies",
        json=AgencyPostRequest(
            name="Test Agency",
            type=AgencyType.LAW_ENFORCEMENT,
            jurisdiction_type=JurisdictionType.STATE,
            location_ids=[california.location_id]
        ).model_dump(mode="json")
    )

    agency: Agency = await ath.adb_client().one_or_none_model(model=Agency)
    assert agency.name == "Test Agency"
    assert agency.agency_type == AgencyType.LAW_ENFORCEMENT
    assert agency.jurisdiction_type == JurisdictionType.STATE

    link: LinkAgencyLocation = await ath.adb_client().one_or_none_model(model=LinkAgencyLocation)
    assert link is not None
    assert link.agency_id == agency.agency_id
    assert link.location_id == california.location_id

    rv.delete_v3(
        url=f"/agencies/{agency.agency_id}/locations/{california.location_id}",
    )

    link: LinkAgencyLocation | None = await ath.adb_client().one_or_none_model(model=LinkAgencyLocation)
    assert link is None

    rv.post_v3(
        url=f"/agencies/{agency.agency_id}/locations/{pennsylvania.location_id}",
    )

    link: LinkAgencyLocation = await ath.adb_client().one_or_none_model(model=LinkAgencyLocation)
    assert link is not None
    assert link.agency_id == agency.agency_id
    assert link.location_id == pennsylvania.location_id

    rv.put_v3(
        url=f"/agencies/{agency.agency_id}",
        json=AgencyPutRequest(
            name="Test Agency Updated",
        ).model_dump(mode="json")
    )

    agency: Agency = await ath.adb_client().one_or_none_model(model=Agency)
    assert agency.name == "Test Agency Updated"
    assert agency.agency_type == AgencyType.LAW_ENFORCEMENT
    assert agency.jurisdiction_type == JurisdictionType.STATE


    rv.delete_v3(
        url=f"/agencies/{agency.agency_id}",
    )

    agency: Agency | None = await ath.adb_client().one_or_none_model(model=Agency)
    assert agency is None
