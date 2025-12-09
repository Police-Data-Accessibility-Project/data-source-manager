import pytest

from src.external.url_request.dtos.screenshot_response import URLScreenshotResponse
from src.external.url_request.screenshot_.core import get_screenshots


@pytest.mark.asyncio
async def test_url_screenshot():
    """
    Note that this will save a file to the working directory
    Be sure to remove it after inspection.
    """

    urls: list[str] = [
        "www.example.com"
    ]

    responses: list[URLScreenshotResponse] = await get_screenshots(urls=urls)
    for idx, response in enumerate(responses):
        with open(f"screenshot_{idx}.webp", "wb") as f:
            f.write(response.screenshot)