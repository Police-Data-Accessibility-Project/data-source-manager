import pytest

from src.db.models.impl.agency.ds_link.sqlalchemy import DSAppLinkAgency
from src.db.models.impl.agency.enums import AgencyType, JurisdictionType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.flag.ds_delete.agency import FlagDSDeleteAgency
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.counter import next_int


@pytest.mark.asyncio
async def test_ds_linked(
    api_test_helper: APITestHelper
):
    """If an agency has been linked to the Data Sources App,
    the deletion operation should include an agency flag for deletion.
    """

    agency = Agency(
        name="Test Agency",
        agency_type=AgencyType.LAW_ENFORCEMENT,
        jurisdiction_type=JurisdictionType.STATE,
    )
    agency_id: int = await api_test_helper.adb_client().add(agency, return_id=True)

    ds_agency_id: int = next_int()
    # Add DS link
    ds_link = DSAppLinkAgency(
        agency_id=agency_id,
        ds_agency_id=ds_agency_id,
    )
    await api_test_helper.adb_client().add(ds_link)

    api_test_helper.request_validator.delete_v3(
        url=f"/agencies/{agency.id}",
    )

    agency: Agency | None = await api_test_helper.adb_client().one_or_none_model(model=Agency)
    assert agency is None

    flag: FlagDSDeleteAgency | None = await api_test_helper.adb_client().one_or_none_model(model=FlagDSDeleteAgency)
    assert flag is not None
    assert flag.ds_agency_id == ds_agency_id

