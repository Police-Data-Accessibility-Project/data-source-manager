from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from src.collectors.manager import AsyncCollectorManager
from src.core.core import AsyncCore
from src.core.logger import AsyncCoreLogger
from src.db.client.async_ import AsyncDatabaseClient
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
def pennsylvania(
    adb_client_test: AsyncDatabaseClient
) -> USStateCreationInfo:
    """Creates Pennsylvania state and returns its state and location ID"""
    raise NotImplementedError

@pytest_asyncio.fixture
def allegheny_county(
    adb_client_test: AsyncDatabaseClient,
    pennsylvania: USStateCreationInfo
) -> CountyCreationInfo:
    raise NotImplementedError

@pytest_asyncio.fixture
def pittsburgh_locality(
    adb_client_test: AsyncDatabaseClient,
    allegheny_county: CountyCreationInfo
) -> LocalityCreationInfo:
    raise NotImplementedError

@pytest_asyncio.fixture
def california(
    adb_client_test: AsyncDatabaseClient
) -> USStateCreationInfo:
    raise NotImplementedError

@pytest_asyncio.fixture
def los_angeles_county(
    adb_client_test: AsyncDatabaseClient,
    california: USStateCreationInfo
) -> CountyCreationInfo:
    raise NotImplementedError

@pytest_asyncio.fixture
def los_angeles_locality(
    adb_client_test: AsyncDatabaseClient,
    los_angeles_county: CountyCreationInfo
) -> LocalityCreationInfo:
    raise NotImplementedError