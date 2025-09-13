from http import HTTPStatus

from fastapi import HTTPException

from src.api.endpoints.url.by_id.screenshot.query import GetURLScreenshotQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient


async def get_url_screenshot_wrapper(
    url_id: int,
    adb_client: AsyncDatabaseClient,
) -> bytes:

    raw_result: bytes | None = await adb_client.run_query_builder(
        GetURLScreenshotQueryBuilder(url_id=url_id)
    )
    if raw_result is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="URL not found"
        )
    return raw_result