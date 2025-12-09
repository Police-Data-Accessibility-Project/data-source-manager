from src.api.endpoints.check.unique_url.response import CheckUniqueURLResponse
from src.db.client.async_ import AsyncDatabaseClient
from src.db.queries.urls_exist.model import URLExistsResult
from src.db.queries.urls_exist.query import URLsExistInDBQueryBuilder
from src.util.models.full_url import FullURL


async def check_unique_url_wrapper(
    adb_client: AsyncDatabaseClient,
    url: str
) -> CheckUniqueURLResponse:
    result: URLExistsResult = (await adb_client.run_query_builder(
        URLsExistInDBQueryBuilder(full_urls=[FullURL(url)])
    ))[0]
    if result.exists:
        return CheckUniqueURLResponse(
            unique_url=False,
            url_id=result.url_id
        )
    return CheckUniqueURLResponse(
        unique_url=True,
        url_id=None
    )
