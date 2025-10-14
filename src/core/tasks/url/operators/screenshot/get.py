from src.core.tasks.url.operators.screenshot.models.outcome import URLScreenshotOutcome
from src.db.dtos.url.mapping import URLMapping
from src.external.url_request.dtos.screenshot_response import URLScreenshotResponse
from src.external.url_request.screenshot_.core import get_screenshots
from src.util.url_mapper import URLMapper


async def get_url_screenshots(mappings: list[URLMapping]) -> list[URLScreenshotOutcome]:
    mapper = URLMapper(mappings)
    responses: list[URLScreenshotResponse] = await get_screenshots(
        urls=mapper.get_all_urls()
    )
    outcomes: list[URLScreenshotOutcome] = []
    for response in responses:
        url_id: int = mapper.get_id(response.url)
        outcome = URLScreenshotOutcome(
            url_id=url_id,
            screenshot=response.screenshot,
            error=response.error,
        )
        outcomes.append(outcome)
    return outcomes
