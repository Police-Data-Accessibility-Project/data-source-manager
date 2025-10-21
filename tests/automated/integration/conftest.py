from typing import Generator, AsyncGenerator, Any
from unittest.mock import MagicMock, AsyncMock

import pytest
import pytest_asyncio
from starlette.testclient import TestClient

from src.api.main import app
from src.collectors.manager import AsyncCollectorManager
from src.core.core import AsyncCore
from src.core.logger import AsyncCoreLogger
from src.db.client.async_ import AsyncDatabaseClient
from src.db.client.sync import DatabaseClient
from src.security.dtos.access_info import AccessInfo
from src.security.enums import Permissions
from src.security.manager import get_access_info
from tests.automated.integration.api._helpers.RequestValidator import RequestValidator
from tests.helpers.api_test_helper import APITestHelper
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


MOCK_USER_ID = 1


async def fail_task_trigger() -> None:
    raise Exception(
        "Task Trigger is set to fail in tests by default, to catch unintentional calls."
        "If this is not intended, either replace with a Mock or the expected task function."
    )


def override_access_info() -> AccessInfo:
    return AccessInfo(
        user_id=MOCK_USER_ID,
        permissions=[
            Permissions.SOURCE_COLLECTOR,
            Permissions.SOURCE_COLLECTOR_FINAL_REVIEW
        ]
    )


@pytest.fixture(scope="session")
def client(disable_task_flags) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        app.dependency_overrides[get_access_info] = override_access_info
        async_core: AsyncCore = c.app.state.async_core

        # Interfaces to the web should be mocked
        task_manager = async_core.task_manager
        task_manager.url_request_interface = AsyncMock()
        task_manager.discord_poster = AsyncMock()
        # Disable Logger
        task_manager.logger.disabled = True
        # Set trigger to fail immediately if called, to force it to be manually specified in tests
        task_manager.task_trigger._func = fail_task_trigger
        yield c

    # Reset environment variables back to original state


@pytest_asyncio.fixture
async def api_test_helper(
    client: TestClient,
    db_client_test: DatabaseClient,
    adb_client_test: AsyncDatabaseClient
) -> AsyncGenerator[APITestHelper, Any]:
    yield APITestHelper(
        request_validator=RequestValidator(client=client),
        async_core=client.app.state.async_core,
        db_data_creator=DBDataCreator(
            db_client=db_client_test,
            adb_client=adb_client_test
        ),
    )
    await client.app.state.async_core.collector_manager.logger.clear_log_queue()

@pytest_asyncio.fixture
async def test_agency_id(
    db_data_creator: DBDataCreator
) -> int:
    return await db_data_creator.agency(
        name="Test Agency"
    )