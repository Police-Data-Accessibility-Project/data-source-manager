from datetime import datetime

import pytest_asyncio

from src.core.tasks.scheduled.impl.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.agency.sqlalchemy import Agency
from src.external.pdap.client import PDAPClient
from tests.helpers.data_creator.core import DBDataCreator


@pytest_asyncio.fixture
async def operator(
    db_data_creator: DBDataCreator,
    mock_pdap_client: PDAPClient
) -> SyncDataSourcesTaskOperator:
    return SyncDataSourcesTaskOperator(
        adb_client=db_data_creator.adb_client,
        pdap_client=mock_pdap_client
    )

@pytest_asyncio.fixture
async def current_db_time(
    adb_client_test: AsyncDatabaseClient
) -> datetime:
    return (await adb_client_test.get_current_database_time()).replace(tzinfo=None)


@pytest_asyncio.fixture
async def agency_ids(
    adb_client_test: AsyncDatabaseClient
) -> list[int]:
    """Creates and returns the ids of 4 agencies"""
    agencies: list[Agency] = []
    agency_ids: list[int] = []
    for i in range(4):
        agency = Agency(
            agency_id=i,
            name=f"Test Agency {i}",
            state="test_state",
            county="test_county",
            locality="test_locality"
        )
        agency_ids.append(i)
        agencies.append(agency)
    await adb_client_test.add_all(agencies)
    return agency_ids
