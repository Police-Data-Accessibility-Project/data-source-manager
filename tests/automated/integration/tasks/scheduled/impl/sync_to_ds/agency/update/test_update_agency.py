from sqlalchemy import update

from src.api.shared.models.message_response import MessageResponse
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.update.core import DSAppSyncAgenciesUpdateTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.agency.ds_link.sqlalchemy import DSAppLinkAgency
from src.db.models.impl.agency.enums import AgencyType, JurisdictionType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.sync.agencies.update.request import UpdateAgenciesOuterRequest
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.helpers import extract_and_validate_sync_request, \
    mock_make_request
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel
from tests.helpers.run import run_task_and_confirm_success


async def test_update_agency(
    ds_app_linked_agency: DSAppLinkInfoModel,
    operator: DSAppSyncAgenciesUpdateTaskOperator,
    mock_pdap_client: PDAPClient,
    adb_client_test: AsyncDatabaseClient
):

    # Check prerequisites not met
    assert not await operator.meets_task_prerequisites()

    # Mock make_request
    mock_make_request(
        mock_pdap_client=mock_pdap_client,
        data=MessageResponse(message="Success")
    )

    # Update agency table
    statement = (
        update(
            Agency
        )
        .values(
            name="Updated Agency Name",
            agency_type=AgencyType.COURT,
            jurisdiction_type=JurisdictionType.STATE
        )
        .where(
            Agency.id == ds_app_linked_agency.db_id
        )
    )
    await adb_client_test.execute(statement)

    # Check prerequisites are met
    assert operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was called with expected parameters
    extract_and_validate_sync_request(
        mock_pdap_client,
        expected_path="agencies/update",
        expected_model=UpdateAgenciesOuterRequest
    )

    # Check DS App Link Is Updated
    ds_app_link: DSAppLinkAgency | None = await adb_client_test.one_or_none_model(model=DSAppLinkAgency)
    assert ds_app_link is not None
    assert ds_app_link.ds_agency_id == 67
    assert ds_app_link.last_synced_at > ds_app_linked_agency.updated_at
