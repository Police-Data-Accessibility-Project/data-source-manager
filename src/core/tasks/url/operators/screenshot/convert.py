from src.core.tasks.url.operators.screenshot.models.outcome import URLScreenshotOutcome
from src.db.models.impl.url.error_info.pydantic import URLErrorInfoPydantic
from src.db.models.impl.url.screenshot.pydantic import URLScreenshotPydantic


def convert_to_url_screenshot_pydantic(
    outcomes: list[URLScreenshotOutcome]
) -> list[URLScreenshotPydantic]:
    raise NotImplementedError

def convert_to_url_error_info(
    outcomes: list[URLScreenshotOutcome]
) -> list[URLErrorInfoPydantic]:
    raise NotImplementedError