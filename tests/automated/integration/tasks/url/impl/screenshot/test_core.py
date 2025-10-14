from unittest.mock import AsyncMock

import pytest

from src.core.tasks.url.operators.screenshot.core import URLScreenshotTaskOperator
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.url.screenshot.sqlalchemy import URLScreenshot
from src.db.models.impl.url.task_error.sqlalchemy import URLTaskError
from src.external.url_request.dtos.screenshot_response import URLScreenshotResponse
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success

# src/core/tasks/url/operators/screenshot/get.py
MOCK_ROOT_PATH = "src.core.tasks.url.operators.screenshot.get.get_screenshots"

@pytest.mark.asyncio
async def test_core(
    operator: URLScreenshotTaskOperator,
    db_data_creator: DBDataCreator,
    monkeypatch
) -> None:

    # Should not yet meet task prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add two URLs to database
    url_mappings: list[URLMapping] = await db_data_creator.create_urls(count=2)
    screenshot_mapping: URLMapping = url_mappings[0]
    error_mapping: URLMapping = url_mappings[1]
    url_ids: list[int] = [url_mapping.url_id for url_mapping in url_mappings]

    # Add web metadata for 200 responses
    await db_data_creator.create_web_metadata(
        url_ids=url_ids,
        status_code=200,
    )

    # Should now meet task prerequisites
    assert await operator.meets_task_prerequisites()

    mock_get_screenshots = AsyncMock(return_value=[
        URLScreenshotResponse(
            url=screenshot_mapping.url,
            screenshot=bytes(124536),
        ),
        URLScreenshotResponse(
            url=error_mapping.url,
            screenshot=None,
            error="error",
        )
    ])

    # Mock get_url_screenshots to return one success and one failure
    monkeypatch.setattr(
        MOCK_ROOT_PATH,
        mock_get_screenshots
    )

    await run_task_and_confirm_success(operator)

    # Get screenshots from database, confirm only one
    screenshots: list[URLScreenshot] = await db_data_creator.adb_client.get_all(URLScreenshot)
    assert len(screenshots) == 1
    assert screenshots[0].url_id == screenshot_mapping.url_id

    # Get errors from database, confirm only one
    errors: list[URLTaskError] = await db_data_creator.adb_client.get_all(URLTaskError)
    assert len(errors) == 1
    assert errors[0].url_id == error_mapping.url_id





