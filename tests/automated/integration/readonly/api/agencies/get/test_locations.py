import pytest

from tests.automated.integration.readonly.helper import ReadOnlyTestHelper


@pytest.mark.asyncio
async def test_agency_get_locations(
    readonly_helper: ReadOnlyTestHelper,
) -> None:

    response_raw: list[dict] = readonly_helper.api_test_helper.request_validator.get_v3(
        url=f"/agencies/{readonly_helper.agency_1_id}/locations",
    )
    assert len(response_raw) == 1
    assert response_raw[0]["location_id"] == readonly_helper.agency_1_location_id
    assert response_raw[0]["full_display_name"] == "Pittsburgh, Allegheny, Pennsylvania"
