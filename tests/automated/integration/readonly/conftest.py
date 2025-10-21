import asyncio
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from pydantic import BaseModel
from starlette.testclient import TestClient

from src.db.client.async_ import AsyncDatabaseClient
from src.db.helpers.connect import get_postgres_connection_string
from src.db.models.impl.agency.enums import AgencyType, JurisdictionType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from tests.automated.integration.api._helpers.RequestValidator import RequestValidator
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.counter import next_int
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo
from tests.helpers.setup.wipe import wipe_database


class ReadOnlyTestHelper(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    adb_client: AsyncDatabaseClient
    api_test_helper: APITestHelper

    agency_1_id: int
    agency_1_location_id: int


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
) -> AsyncGenerator[ReadOnlyTestHelper, Any]:
    wipe_database(get_postgres_connection_string())
    conn = get_postgres_connection_string(is_async=True)
    adb_client = AsyncDatabaseClient(db_url=conn)
    db_data_creator = DBDataCreator()
    api_test_helper = APITestHelper(
        request_validator=RequestValidator(client=client),
        async_core=client.app.state.async_core,
        db_data_creator=db_data_creator,
    )

    # Pennsylvania
    pennsylvania = await DBDataCreator().create_us_state(
        name="Pennsylvania",
        iso="PA"
    )

    allegheny_county = await DBDataCreator().create_county(
        state_id=pennsylvania.us_state_id,
        name="Allegheny"
    )
    pittsburgh = await DBDataCreator().create_locality(
        state_id=pennsylvania.us_state_id,
        county_id=allegheny_county.county_id,
        name="Pittsburgh"
    )


    # Add Agencies
    agency_1 = Agency(
        agency_id=next_int(),
        name="Agency 1",
        agency_type=AgencyType.LAW_ENFORCEMENT,
        jurisdiction_type=JurisdictionType.STATE,
    )
    await adb_client.add(agency_1)

    # Add Agency location
    agency_1_location = LinkAgencyLocation(
        agency_id=agency_1.agency_id,
        location_id=pittsburgh.location_id,
    )
    await adb_client.add(agency_1_location)

    yield ReadOnlyTestHelper(
        adb_client=adb_client,
        api_test_helper=api_test_helper,

        agency_1_id=agency_1.agency_id,
        agency_1_location_id=pittsburgh.location_id,
    )