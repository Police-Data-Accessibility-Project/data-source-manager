import pytest

from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.add.core import DSAppSyncMetaURLsAddTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from src.external.pdap.client import PDAPClient
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_add(
    db_data_creator: DBDataCreator,
    test_url_meta_url_id: int,
    adb_client_test: AsyncDatabaseClient,
    mock_pdap_client: PDAPClient
):
    operator = DSAppSyncMetaURLsAddTaskOperator(
        adb_client=adb_client_test,
        pdap_client=mock_pdap_client
    )

    # Check meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was called with expected parameters

    # Check Presence of DS Meta URL App Link
    ds_app_link: DSAppLinkMetaURL = await adb_client_test.one_or_none_model(model=DSAppLinkMetaURL)
    assert ds_app_link is not None
    assert ds_app_link.url_id == test_url_meta_url_id
