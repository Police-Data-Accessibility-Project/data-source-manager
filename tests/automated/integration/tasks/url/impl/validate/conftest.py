import pytest
import pytest_asyncio

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from tests.automated.integration.tasks.url.impl.validate.helper import TestValidateTaskHelper
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo


@pytest.fixture
def operator(
    adb_client_test: AsyncDatabaseClient
) -> AutoValidateURLTaskOperator:
    return AutoValidateURLTaskOperator(
        adb_client=adb_client_test,
    )

@pytest_asyncio.fixture
async def helper(
    db_data_creator: DBDataCreator,
    pittsburgh_locality: LocalityCreationInfo
) -> TestValidateTaskHelper:
    url_id: int = (await db_data_creator.create_urls(count=1, record_type=None))[0].url_id
    agency_id: int = await db_data_creator.agency()
    return TestValidateTaskHelper(
        db_data_creator,
        url_id=url_id,
        agency_id=agency_id,
        location_id=pittsburgh_locality.location_id
    )

