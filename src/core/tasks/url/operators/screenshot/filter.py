from src.core.tasks.url.operators.screenshot.models.outcome import URLScreenshotOutcome
from src.core.tasks.url.operators.screenshot.models.subsets import URLScreenshotOutcomeSubsets


def filter_success_outcomes(outcomes: list[URLScreenshotOutcome]) -> URLScreenshotOutcomeSubsets:
    raise NotImplementedError