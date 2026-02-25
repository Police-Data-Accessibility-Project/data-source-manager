import pytest_asyncio
from sqlalchemy import Engine
from starlette.testclient import TestClient

from tests.automated.integration.api._helpers.RequestValidator import RequestValidator
from tests.automated.integration.benchmark.scale_seed import ScaleSeedResult, create_scale_data
from tests.automated.integration.readonly.helper import ReadOnlyTestHelper
from tests.automated.integration.readonly.setup.core import setup_readonly_data
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.setup.wipe import wipe_database


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def benchmark_readonly_helper(
    client: TestClient, engine: Engine
) -> ReadOnlyTestHelper:
    wipe_database(engine)
    db_data_creator = DBDataCreator()
    api_test_helper = APITestHelper(
        request_validator=RequestValidator(client=client),
        async_core=client.app.state.async_core,
        db_data_creator=db_data_creator,
    )
    return await setup_readonly_data(api_test_helper=api_test_helper)


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def scale_seeder(client: TestClient, engine: Engine) -> ScaleSeedResult:
    """Seed 10k URLs once per session for scale benchmarks."""
    wipe_database(engine)
    db_data_creator = DBDataCreator()
    api_test_helper = APITestHelper(
        request_validator=RequestValidator(client=client),
        async_core=client.app.state.async_core,
        db_data_creator=db_data_creator,
    )
    adb_client = db_data_creator.adb_client
    return await create_scale_data(
        adb_client=adb_client,
        db_data_creator=db_data_creator,
        api_test_helper=api_test_helper,
    )
