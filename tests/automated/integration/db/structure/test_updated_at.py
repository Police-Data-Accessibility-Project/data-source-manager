import asyncio
from datetime import datetime

import pytest

from src.collectors.enums import URLStatus
from src.db.models.impl.url.core.pydantic.upsert import URLUpsertModel
from src.db.models.impl.url.core.sqlalchemy import URL
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_updated_at(db_data_creator: DBDataCreator):

    _ = await db_data_creator.create_urls(
        count=1,
        status=URLStatus.OK
    )

    urls: list[URL] = await db_data_creator.adb_client.get_all(URL)
    url = urls[0]
    assert url.updated_at is not None
    updated_at: datetime = url.updated_at

    url_upsert = URLUpsertModel(
        id=url.id,
        name="New Name",
        url=url.url,
        trailing_slash=url.trailing_slash,
    )

    await db_data_creator.adb_client.bulk_update([url_upsert])

    new_urls: list[URL] = await db_data_creator.adb_client.get_all(URL)
    new_url = new_urls[0]

    new_updated_at = new_url.updated_at
    assert new_updated_at > updated_at


