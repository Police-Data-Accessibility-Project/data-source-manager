import pytest

from src.api.shared.models.message_response import MessageResponse
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.delete.core import DSAppSyncAgenciesDeleteTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.agency.ds_link.sqlalchemy import DSAppLinkAgency
from src.db.models.impl.flag.ds_delete.agency import FlagDSDeleteAgency
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.sync.shared.models.delete.request import DSAppSyncDeleteRequestModel
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.helpers import extract_and_validate_sync_request, \
    mock_make_request
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_delete(
    db_data_creator: DBDataCreator,
    ds_app_linked_agency: DSAppLinkInfoModel,
    adb_client_test: AsyncDatabaseClient,
    mock_pdap_client: PDAPClient
):
    ds_agency_id: int = 67
    operator = DSAppSyncAgenciesDeleteTaskOperator(
        adb_client=adb_client_test,
        pdap_client=mock_pdap_client
    )

    # Mock make_request
    mock_make_request(
        mock_pdap_client=mock_pdap_client,
        data=MessageResponse(message="Success")
    )


    # Check does not currently meet prerequisite
    assert not await operator.meets_task_prerequisites()

    # Add Task Deletion Flag for App Link
    flag = FlagDSDeleteAgency(
        ds_agency_id=ds_agency_id
    )
    await adb_client_test.add(flag)

    # Check meets prerequisite
    assert operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was caused with expected parameters
    request: DSAppSyncDeleteRequestModel = extract_and_validate_sync_request(
        mock_pdap_client,
        expected_path="agencies/delete",
        expected_model=DSAppSyncDeleteRequestModel
    )
    assert request.ids == [ds_agency_id]

    # Check DS App Link Is Deleted
    assert await adb_client_test.has_no_rows(DSAppLinkAgency)

    # Check DS App Agency Deletion Flag is deleted
    assert await adb_client_test.has_no_rows(FlagDSDeleteAgency)
