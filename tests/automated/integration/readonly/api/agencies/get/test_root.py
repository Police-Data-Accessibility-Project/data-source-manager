import pytest

from src.db.models.impl.agency.enums import JurisdictionType, AgencyType
from tests.automated.integration.readonly.helper import ReadOnlyTestHelper


@pytest.mark.asyncio
async def test_agency_get(
    readonly_helper: ReadOnlyTestHelper
):

    responses_raw: list[dict] = readonly_helper.api_test_helper.request_validator.get_v3(
        url=f"/agencies",
    )
    assert len(responses_raw) == 2
    response_raw = responses_raw[0]
    assert response_raw["id"] == readonly_helper.agency_1_id
    assert response_raw["name"] == "Agency 1"
    assert response_raw["type"] == AgencyType.LAW_ENFORCEMENT.value
    assert response_raw["jurisdiction_type"] == JurisdictionType.STATE.value