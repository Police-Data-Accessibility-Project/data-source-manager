from src.core.tasks.url.operators.screenshot.models.outcome import URLScreenshotOutcome
from src.db.models.impl.url.screenshot.pydantic import URLScreenshotPydantic
from src.db.models.impl.url.task_error.pydantic_.small import URLTaskErrorSmall


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

def convert_to_task_error(
    outcomes: list[URLScreenshotOutcome]
) -> list[URLTaskErrorSmall]:
    results: list[URLTaskErrorSmall] = []
    for outcome in outcomes:
        result = URLTaskErrorSmall(
            url_id=outcome.url_id,
            error=outcome.error,
        )
        results.append(result)
    return results
