import pytest_asyncio
from sqlalchemy import Engine
from starlette.testclient import TestClient

from tests.automated.integration.api._helpers.RequestValidator import RequestValidator
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
