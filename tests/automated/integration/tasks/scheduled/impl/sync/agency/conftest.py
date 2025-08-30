import pytest_asyncio

from src.core.tasks.scheduled.impl.sync.agency.operator import SyncAgenciesTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.external.pdap.client import PDAPClient
from tests.automated.integration.tasks.scheduled.impl.sync.agency.helpers import update_existing_agencies_updated_at, \
    add_existing_agencies


@pytest_asyncio.fixture
async def operator(
    adb_client_test: AsyncDatabaseClient,
    mock_pdap_client: PDAPClient
) -> SyncAgenciesTaskOperator:
    return SyncAgenciesTaskOperator(
        adb_client=adb_client_test,
        pdap_client=mock_pdap_client
    )

@pytest_asyncio.fixture
async def setup(
    db_data_creator,
    operator
) -> SyncAgenciesTaskOperator:
    await add_existing_agencies(db_data_creator)
    await update_existing_agencies_updated_at(db_data_creator)

    return operator


