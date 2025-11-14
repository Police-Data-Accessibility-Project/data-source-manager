import pytest

from src.api.shared.models.message_response import MessageResponse
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.delete.core import \
    DSAppSyncDataSourcesDeleteTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.ds_delete.data_source import FlagDSDeleteDataSource
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.sync.shared.models.delete.request import DSAppSyncDeleteRequestModel
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.helpers import extract_and_validate_sync_request, \
    mock_make_request
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_delete(
    db_data_creator: DBDataCreator,
    adb_client_test: AsyncDatabaseClient,
    mock_pdap_client: PDAPClient
):
    ds_data_source_id: int = 67
    operator = DSAppSyncDataSourcesDeleteTaskOperator(
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

    # Add DS App Link
    ds_app_link = DSAppLinkDataSource(
        url_id=None,
        ds_data_source_id=ds_data_source_id,
    )
    await adb_client_test.add(ds_app_link)

    # Add Task Deletion Flag for App Link
    flag = FlagDSDeleteDataSource(
        ds_data_source_id=ds_data_source_id,
    )
    await adb_client_test.add(flag)

    # Check meets prerequisite
    assert operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was caused with expected parameters
    request: DSAppSyncDeleteRequestModel = extract_and_validate_sync_request(
        mock_pdap_client,
        expected_path="data-sources/delete",
        expected_model=DSAppSyncDeleteRequestModel
    )
    assert request.ids == [ds_data_source_id]

    # Check DS App Link Is Deleted
    assert await adb_client_test.has_no_rows(DSAppLinkDataSource)

    # Check DS App Data Source Deletion Flag is deleted
    assert await adb_client_test.has_no_rows(FlagDSDeleteDataSource)
