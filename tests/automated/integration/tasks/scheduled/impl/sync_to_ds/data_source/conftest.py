import pytest_asyncio

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel


@pytest_asyncio.fixture
async def ds_app_linked_data_source_url(
    test_url_data_source_id: int,
    adb_client_test: AsyncDatabaseClient
) -> DSAppLinkInfoModel:
    link = DSAppLinkDataSource(
        ds_data_source_id=67,
        url_id=test_url_data_source_id,
    )
    await adb_client_test.add(link)
    return DSAppLinkInfoModel(
        db_id=test_url_data_source_id,
        ds_app_id=67,
    )