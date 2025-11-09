import pytest_asyncio

from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel


@pytest_asyncio.fixture
async def ds_app_linked_agency(
    test_agency_id: int
) -> DSAppLinkInfoModel:
    raise NotImplementedError