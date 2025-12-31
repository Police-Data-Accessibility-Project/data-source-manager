from typing import Generator, AsyncGenerator, Any
from unittest.mock import MagicMock, AsyncMock

import pytest
import pytest_asyncio
from starlette.testclient import TestClient

from src.api.main import app
from src.collectors.enums import URLStatus
from src.collectors.manager import AsyncCollectorManager
from src.core.core import AsyncCore
from src.core.enums import RecordType
from src.core.logger import AsyncCoreLogger
from src.db.client.async_ import AsyncDatabaseClient
from src.db.client.sync import DatabaseClient
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.security.dtos.access_info import AccessInfo
from src.security.enums import Permissions
from src.security.manager import get_access_info, get_standard_user_access_info
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
        app.dependency_overrides[get_standard_user_access_info] = override_access_info
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

@pytest.fixture
def test_batch_id(
    db_data_creator: DBDataCreator
) -> int:
    return db_data_creator.batch()

@pytest_asyncio.fixture
async def test_agency_id(
    db_data_creator: DBDataCreator,
    pittsburgh_locality: LocalityCreationInfo,
    pennsylvania: USStateCreationInfo
) -> int:
    """Test agency linked to two locations: Pittsburgh and Pennsylvania"""
    agency_id: int = await db_data_creator.agency(
        name="Test Agency"
    )
    await db_data_creator.link_agencies_to_location(
        agency_ids=[agency_id],
        location_id=pittsburgh_locality.location_id
    )
    await db_data_creator.link_agencies_to_location(
        agency_ids=[agency_id],
        location_id=pennsylvania.location_id
    )
    return agency_id

@pytest_asyncio.fixture
async def test_agency_id_2(
    db_data_creator: DBDataCreator,
    pittsburgh_locality: LocalityCreationInfo
) -> int:
    agency_id: int = await db_data_creator.agency(
        name="Test Agency 2"
    )
    await db_data_creator.link_agencies_to_location(
        agency_ids=[agency_id],
        location_id=pittsburgh_locality.location_id
    )
    return agency_id

@pytest_asyncio.fixture
async def test_url_data_source_id(
    db_data_creator: DBDataCreator,
    test_agency_id: int
) -> int:
    url_id: int = (await db_data_creator.create_validated_urls(
        record_type=RecordType.CRIME_STATISTICS,
        validation_type=URLType.DATA_SOURCE,
    ))[0].url_id
    await db_data_creator.link_urls_to_agencies(
        url_ids=[url_id],
        agency_ids=[test_agency_id]
    )
    return url_id

@pytest_asyncio.fixture
async def test_url_data_source_id_2(
    db_data_creator: DBDataCreator,
    test_agency_id: int
) -> int:
    url_id: int = (await db_data_creator.create_validated_urls(
        record_type=RecordType.CAR_GPS,
        validation_type=URLType.DATA_SOURCE,
    ))[0].url_id
    await db_data_creator.link_urls_to_agencies(
        url_ids=[url_id],
        agency_ids=[test_agency_id]
    )
    return url_id

@pytest_asyncio.fixture
async def test_url_id(
    db_data_creator: DBDataCreator,
) -> int:
    url = URL(
        url="example.com",
        source=URLSource.COLLECTOR,
        trailing_slash=False,
    )
    return await db_data_creator.adb_client.add(url, return_id=True)

@pytest_asyncio.fixture
async def test_url_id_2(
    db_data_creator: DBDataCreator,
) -> int:
    url = URL(
        url="example.com/2",
        source=URLSource.COLLECTOR,
        trailing_slash=False,
        status=URLStatus.OK
    )
    return await db_data_creator.adb_client.add(url, return_id=True)


@pytest_asyncio.fixture
async def test_url_data_source_mapping(
    db_data_creator: DBDataCreator,
    test_agency_id: int
) -> SimpleURLMapping:
    url_mapping: SimpleURLMapping = (await db_data_creator.create_validated_urls(
        record_type=RecordType.CRIME_STATISTICS,
        validation_type=URLType.DATA_SOURCE,
    ))[0]
    await db_data_creator.link_urls_to_agencies(
        url_ids=[url_mapping.url_id],
        agency_ids=[test_agency_id]
    )
    return url_mapping

@pytest_asyncio.fixture
async def test_url_meta_url_id(
    db_data_creator: DBDataCreator,
    test_agency_id: int
) -> int:
    url_id: int = (await db_data_creator.create_validated_urls(
        validation_type=URLType.META_URL,
    ))[0].url_id
    await db_data_creator.link_urls_to_agencies(
        url_ids=[url_id],
        agency_ids=[test_agency_id]
    )
    return url_id
