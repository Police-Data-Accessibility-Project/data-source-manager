from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from src.collectors.manager import AsyncCollectorManager
from src.core.core import AsyncCore
from src.core.logger import AsyncCoreLogger
from src.db.client.async_ import AsyncDatabaseClient
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo


@pytest.fixture
def test_async_core(adb_client_test):
    logger = AsyncCoreLogger(
        adb_client=adb_client_test
    )
    adb_client = AsyncDatabaseClient()
    core = AsyncCore(
        adb_client=adb_client,
        task_manager=MagicMock(),
        collector_manager=AsyncCollectorManager(
            adb_client=adb_client,
            logger=logger,
            dev_mode=True
        ),
    )
    yield core
    core.shutdown()
    logger.shutdown()

@pytest_asyncio.fixture
async def pennsylvania(
    db_data_creator: DBDataCreator
) -> USStateCreationInfo:
    """Creates Pennsylvania state and returns its state and location ID"""
    return await db_data_creator.create_us_state(
        name="Pennsylvania",
        iso="PA"
    )

@pytest_asyncio.fixture
async def allegheny_county(
    db_data_creator: DBDataCreator,
    pennsylvania: USStateCreationInfo
) -> CountyCreationInfo:
    return await db_data_creator.create_county(
        state_id=pennsylvania.us_state_id,
        name="Allegheny"
    )

@pytest_asyncio.fixture
async def pittsburgh_locality(
    db_data_creator: DBDataCreator,
    pennsylvania: USStateCreationInfo,
    allegheny_county: CountyCreationInfo
) -> LocalityCreationInfo:
    return await db_data_creator.create_locality(
        state_id=pennsylvania.us_state_id,
        county_id=allegheny_county.county_id,
        name="Pittsburgh"
    )

@pytest_asyncio.fixture
async def california(
    db_data_creator: DBDataCreator,
) -> USStateCreationInfo:
    return await db_data_creator.create_us_state(
        name="California",
        iso="CA"
    )

@pytest_asyncio.fixture
async def los_angeles_county(
    db_data_creator: DBDataCreator,
    california: USStateCreationInfo
) -> CountyCreationInfo:
    return await db_data_creator.create_county(
        state_id=california.us_state_id,
        name="Los Angeles"
    )

@pytest_asyncio.fixture
async def los_angeles_locality(
    db_data_creator: DBDataCreator,
    california: USStateCreationInfo,
    los_angeles_county: CountyCreationInfo
) -> LocalityCreationInfo:
    return await db_data_creator.create_locality(
        state_id=california.us_state_id,
        county_id=los_angeles_county.county_id,
        name="Los Angeles"
    )