import pytest

from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.delete.core import DSAppSyncMetaURLsDeleteTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.ds_delete.meta_url import FlagDSDeleteMetaURL
from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from src.external.pdap.client import PDAPClient
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_delete(
    db_data_creator: DBDataCreator,
    adb_client_test: AsyncDatabaseClient,
    mock_pdap_client: PDAPClient
):
    operator = DSAppSyncMetaURLsDeleteTaskOperator(
        adb_client=adb_client_test,
        pdap_client=mock_pdap_client
    )

    # Check does not currently meet prerequisite
    assert not operator.meets_task_prerequisites()

    # Add DS App Link
    ds_app_link = DSAppLinkMetaURL(
        ds_meta_url_id=1,
        url_id=None,
    )
    await adb_client_test.add(ds_app_link)

    # Add Task Deletion Flag for App Link
    flag = FlagDSDeleteMetaURL(
        ds_meta_url_id=1
    )
    await adb_client_test.add(flag)

    # Check meets prerequisite
    assert operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Check DS App Link Is Deleted
    assert await adb_client_test.has_no_rows(DSAppLinkMetaURL)

    # Check DS App Meta URL Deletion Flag is deleted
    assert await adb_client_test.has_no_rows(FlagDSDeleteMetaURL)
