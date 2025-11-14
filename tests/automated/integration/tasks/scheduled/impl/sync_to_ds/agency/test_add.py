import pytest

from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.add.core import DSAppSyncAgenciesAddTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.agency.ds_link.sqlalchemy import DSAppLinkAgency
from src.db.models.impl.agency.enums import JurisdictionType, AgencyType
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.sync.agencies._shared.models.content import AgencySyncContentModel
from src.external.pdap.impl.sync.agencies.add.request import AddAgenciesOuterRequest, AddAgenciesInnerRequest
from src.external.pdap.impl.sync.shared.models.add.response import DSAppSyncAddResponseModel, \
    DSAppSyncAddResponseInnerModel
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.helpers import extract_and_validate_sync_request, \
    mock_make_request
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_add(
    db_data_creator: DBDataCreator,
    test_agency_id: int,
    adb_client_test: AsyncDatabaseClient,
    mock_pdap_client: PDAPClient,
    pittsburgh_locality: LocalityCreationInfo,
    pennsylvania: USStateCreationInfo,
):
    operator = DSAppSyncAgenciesAddTaskOperator(
        adb_client=adb_client_test,
        pdap_client=mock_pdap_client
    )

    # Mock make_request to return a false DS App id
    mock_make_request(
        mock_pdap_client=mock_pdap_client,
        data=DSAppSyncAddResponseModel(
            entities=[
                DSAppSyncAddResponseInnerModel(
                    app_id=67,
                    request_id=test_agency_id
                )
            ]
        )
    )

    # Check meets prerequisite
    assert await operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was called with expected parameters
    request: AddAgenciesOuterRequest = extract_and_validate_sync_request(
        mock_pdap_client,
        expected_path="agencies/add",
        expected_model=AddAgenciesOuterRequest
    )
    assert len(request.agencies) == 1
    agency: AddAgenciesInnerRequest = request.agencies[0]
    assert agency.request_id == test_agency_id
    content: AgencySyncContentModel = agency.content
    assert content.name == "Test Agency"
    assert content.jurisdiction_type == JurisdictionType.LOCAL
    assert content.agency_type == AgencyType.UNKNOWN
    assert set(content.location_ids) == {
        pittsburgh_locality.location_id,
        pennsylvania.location_id
    }

    # Check Presence of DS App Link
    ds_app_link: DSAppLinkAgency = await adb_client_test.one_or_none_model(DSAppLinkAgency)
    assert ds_app_link is not None
    assert ds_app_link.ds_agency_id == 67
    assert ds_app_link.agency_id == test_agency_id


