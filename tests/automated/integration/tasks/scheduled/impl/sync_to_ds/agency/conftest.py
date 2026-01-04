import pytest_asyncio

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.agency.ds_link.sqlalchemy import DSAppLinkAgency
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel


@pytest_asyncio.fixture
async def ds_app_linked_agency(
    test_agency_id: int,
    adb_client_test: AsyncDatabaseClient
) -> DSAppLinkInfoModel:
    # Add DS App Link
    ds_app_link = DSAppLinkAgency(
        agency_id=test_agency_id,
        ds_agency_id=67
    )
    await adb_client_test.add(ds_app_link)
    return DSAppLinkInfoModel(
        ds_app_id=67,
        db_id=test_agency_id
    )
