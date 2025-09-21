import pytest_asyncio

from src.db.dtos.url.mapping import URLMapping
from tests.helpers.data_creator.core import DBDataCreator


@pytest_asyncio.fixture
async def url_ids(
    db_data_creator: DBDataCreator,
) -> list[int]:
    # Create 2 URLs with compressed HTML
    url_mappings: list[URLMapping] = await db_data_creator.create_urls(count=2)
    url_ids: list[int] = [url.url_id for url in url_mappings]
    await db_data_creator.html_data(url_ids=url_ids)
    return url_ids
