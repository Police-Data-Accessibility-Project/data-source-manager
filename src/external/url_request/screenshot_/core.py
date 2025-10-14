from playwright.async_api import async_playwright, Browser, ViewportSize, Page
from tqdm.asyncio import tqdm_asyncio

from src.external.url_request.constants import NETWORK_IDLE
from src.external.url_request.dtos.screenshot_response import URLScreenshotResponse
from src.external.url_request.screenshot_.constants import SCREENSHOT_HEIGHT, SCREENSHOT_WIDTH
from src.external.url_request.screenshot_.convert import convert_png_to_webp
from src.util.progress_bar import get_progress_bar_disabled


async def get_screenshots(
    urls: list[str]
) -> list[URLScreenshotResponse]:
    responses: list[URLScreenshotResponse] = []
    async with async_playwright() as playwright:
        browser: Browser = await playwright.chromium.launch(headless=True)
        page: Page = await browser.new_page(
            viewport=ViewportSize(
                {
                    "width": SCREENSHOT_WIDTH,
                    "height": SCREENSHOT_HEIGHT,
                }
            )
        )
        for url in tqdm_asyncio(urls, disable=get_progress_bar_disabled()):
            try:
                response: URLScreenshotResponse = await get_screenshot(
                    page=page, url=url
                )
                responses.append(response)
            except Exception as e:
                responses.append(
                    URLScreenshotResponse(
                        url=url,
                        screenshot=None,
                        error=str(e)
                    )
                )
        await page.close()
        await browser.close()
    return responses

async def get_screenshot(
    page: Page,
    url: str,
) -> URLScreenshotResponse:
    await page.goto(url)
    await page.wait_for_load_state(NETWORK_IDLE)
    screenshot_png: bytes = await page.screenshot(type="png")
    screenshot_webp: bytes = convert_png_to_webp(screenshot_png)
    return URLScreenshotResponse(
        url=url,
        screenshot=screenshot_webp,
    )
