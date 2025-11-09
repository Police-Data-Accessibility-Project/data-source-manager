import pytest

from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.add.core import DSAppSyncDataSourcesAddTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.external.pdap.client import PDAPClient
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_add(
    db_data_creator: DBDataCreator,
    test_url_data_source_id: int,
    adb_client_test: AsyncDatabaseClient,
    mock_pdap_client: PDAPClient
):
    operator = DSAppSyncDataSourcesAddTaskOperator(
        adb_client=adb_client_test,
        pdap_client=mock_pdap_client
    )

    # Check meet task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was called with expected parameters

    # Check Presence of DS App Link





    raise NotImplementedError