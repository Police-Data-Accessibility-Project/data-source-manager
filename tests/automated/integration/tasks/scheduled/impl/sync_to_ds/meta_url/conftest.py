import pytest_asyncio

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel


@pytest_asyncio.fixture
async def ds_app_linked_meta_url(
    test_url_meta_url_id: int,
    adb_client_test: AsyncDatabaseClient
) -> DSAppLinkInfoModel:
    ds_app_link = DSAppLinkMetaURL(
        url_id=test_url_meta_url_id,
        ds_meta_url_id=1
    )
    await adb_client_test.add(ds_app_link)
    return DSAppLinkInfoModel(
        ds_app_id=1,
    )
