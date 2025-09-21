import pytest_asyncio

from tests.helpers.data_creator.core import DBDataCreator


@pytest_asyncio.fixture
async def url_id(
    db_data_creator: DBDataCreator,
) -> int:
    return (await db_data_creator.create_urls(count=1))[0].url_id
