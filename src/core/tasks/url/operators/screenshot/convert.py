from src.core.tasks.url.operators.screenshot.models.outcome import URLScreenshotOutcome
from src.db.models.impl.url.error.url_screenshot.pydantic import ErrorURLScreenshotPydantic
from src.db.models.impl.url.error_info.pydantic import URLErrorInfoPydantic
from src.db.models.impl.url.screenshot.pydantic import URLScreenshotPydantic


def convert_to_url_screenshot_pydantic(
    outcomes: list[URLScreenshotOutcome]
) -> list[URLScreenshotPydantic]:
    results: list[URLScreenshotPydantic] = []
    for outcome in outcomes:
        result = URLScreenshotPydantic(
            url_id=outcome.url_id,
            content=outcome.screenshot,
            file_size=len(outcome.screenshot),
        )
        results.append(result)
    return results

def convert_to_error_url_screenshot_pydantic(
    outcomes: list[URLScreenshotOutcome]
) -> list[ErrorURLScreenshotPydantic]:
    results: list[ErrorURLScreenshotPydantic] = []
    for outcome in outcomes:
        result = ErrorURLScreenshotPydantic(
            url_id=outcome.url_id,
            error=outcome.error,
        )
        results.append(result)
    return results
