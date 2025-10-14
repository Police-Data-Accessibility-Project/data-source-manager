from pydantic import BaseModel

from src.core.tasks.url.operators.screenshot.models.outcome import URLScreenshotOutcome


class URLScreenshotOutcomeSubsets(BaseModel):
    success: list[URLScreenshotOutcome]
    failed: list[URLScreenshotOutcome]