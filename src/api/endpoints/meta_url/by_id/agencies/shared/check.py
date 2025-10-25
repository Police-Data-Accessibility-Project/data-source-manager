from src.api.shared.check.url_type.query import CheckURLTypeQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_validated.enums import URLType


async def check_is_meta_url(
    url_id: int,
    adb_client: AsyncDatabaseClient
) -> None:
    """
    Raises:
        Bad Request if url_type is not valid or does not exist
    """

    await adb_client.run_query_builder(
        CheckURLTypeQueryBuilder(url_id=url_id, url_type=URLType.META_URL)
    )