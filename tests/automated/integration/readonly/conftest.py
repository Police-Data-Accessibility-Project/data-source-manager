import asyncio
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import Engine
from starlette.testclient import TestClient

from src.db.helpers.connect import get_postgres_connection_string
from tests.automated.integration.api._helpers.RequestValidator import RequestValidator
from tests.automated.integration.readonly.helper import ReadOnlyTestHelper
from tests.automated.integration.readonly.setup import setup_readonly_data
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo
from tests.helpers.setup.wipe import wipe_database


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope='module')
async def california_readonly(
) -> USStateCreationInfo:
    return await DBDataCreator().create_us_state(
        name="California",
        iso="CA"
    )

@pytest_asyncio.fixture(scope="module")
async def readonly_helper(
    event_loop,
    client: TestClient,
    engine: Engine

) -> AsyncGenerator[ReadOnlyTestHelper, Any]:
    wipe_database(engine)
    db_data_creator = DBDataCreator()
    api_test_helper = APITestHelper(
        request_validator=RequestValidator(client=client),
        async_core=client.app.state.async_core,
        db_data_creator=db_data_creator,
    )

    helper: ReadOnlyTestHelper = await setup_readonly_data(api_test_helper=api_test_helper)

    yield helper