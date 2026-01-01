from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from tests.helpers.data_creator.core import DBDataCreator


async def add_meta_url(
    agency_1_id: int,
    db_data_creator: DBDataCreator
) -> int:
    adb_client: AsyncDatabaseClient = db_data_creator.adb_client
    url = URL(
        scheme=None,
        url="read-only-meta-url.com",
        name="Read only URL Name",
        trailing_slash=False,
        description="Read only URL",
        collector_metadata={
            "url": "https://read-only-meta-url.com/"
        },
        source=URLSource.REDIRECT,
    )
    url_id: int = await adb_client.add(url, return_id=True)

    await db_data_creator.create_validated_flags(
        url_ids=[url_id],
        validation_type=URLType.META_URL
    )

    return url_id
