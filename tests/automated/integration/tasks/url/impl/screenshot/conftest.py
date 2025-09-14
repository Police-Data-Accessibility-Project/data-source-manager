import pytest_asyncio

from src.core.tasks.url.operators.screenshot.core import URLScreenshotTaskOperator
from src.db.client.async_ import AsyncDatabaseClient


@pytest_asyncio.fixture
async def operator(
    adb_client_test: AsyncDatabaseClient,
) -> URLScreenshotTaskOperator:
    operator = URLScreenshotTaskOperator(
        adb_client=adb_client_test,
    )
    return operator