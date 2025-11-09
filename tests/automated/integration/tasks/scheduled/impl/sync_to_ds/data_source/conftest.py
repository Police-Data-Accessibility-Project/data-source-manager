import pytest_asyncio

from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel


@pytest_asyncio.fixture
async def ds_app_linked_data_source_url(
    test_url_data_source_id: int,
) -> DSAppLinkInfoModel:
    raise NotImplementedError