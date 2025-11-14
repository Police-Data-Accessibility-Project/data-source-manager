from sqlalchemy import delete

from src.api.shared.models.message_response import MessageResponse
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.update.core import DSAppSyncAgenciesUpdateTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.agency.ds_link.sqlalchemy import DSAppLinkAgency
from src.db.models.impl.agency.enums import JurisdictionType, AgencyType
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.sync.agencies._shared.models.content import AgencySyncContentModel
from src.external.pdap.impl.sync.agencies.update.request import UpdateAgenciesOuterRequest, UpdateAgenciesInnerRequest
from tests.automated.integration.conftest import pennsylvania
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.helpers import extract_and_validate_sync_request, \
    mock_make_request
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo
from tests.helpers.run import run_task_and_confirm_success


async def test_delete_location_link(
    ds_app_linked_agency: DSAppLinkInfoModel,
    pittsburgh_locality: LocalityCreationInfo,
    operator: DSAppSyncAgenciesUpdateTaskOperator,
    mock_pdap_client: PDAPClient,
    pennsylvania: USStateCreationInfo,
    adb_client_test: AsyncDatabaseClient
):

    # Check prerequisites not met
    assert not await operator.meets_task_prerequisites()

    # Mock make_request
    mock_make_request(
        mock_pdap_client=mock_pdap_client,
        data=MessageResponse(message="Success")
    )

    # Delete location link (pittsburgh)
    statement = (
        delete(
            LinkAgencyLocation
        )
        .where(
            LinkAgencyLocation.agency_id == ds_app_linked_agency.db_id,
            LinkAgencyLocation.location_id == pittsburgh_locality.location_id
        )
    )
    await adb_client_test.execute(statement)

    # Check prerequisites are met
    assert operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was called with expected parameters
    request: UpdateAgenciesOuterRequest = extract_and_validate_sync_request(
        mock_pdap_client,
        expected_path="agencies/update",
        expected_model=UpdateAgenciesOuterRequest
    )
    assert len(request.agencies) == 1
    agency: UpdateAgenciesInnerRequest = request.agencies[0]
    assert agency.app_id == ds_app_linked_agency.ds_app_id
    content: AgencySyncContentModel = agency.content
    assert content.name == "Test Agency"
    assert content.jurisdiction_type == JurisdictionType.LOCAL
    assert content.agency_type == AgencyType.UNKNOWN
    assert content.location_ids == [pennsylvania.location_id]

    # Check DS App Link Is Updated
    ds_app_link: DSAppLinkAgency | None = await adb_client_test.one_or_none_model(model=DSAppLinkAgency)
    assert ds_app_link is not None
    assert ds_app_link.ds_agency_id == 67
    assert ds_app_link.last_synced_at > ds_app_linked_agency.updated_at