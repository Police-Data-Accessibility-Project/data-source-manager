from src.core.tasks.url.operators.screenshot.models.outcome import URLScreenshotOutcome
from src.core.tasks.url.operators.screenshot.models.subsets import URLScreenshotOutcomeSubsets


def filter_success_outcomes(outcomes: list[URLScreenshotOutcome]) -> URLScreenshotOutcomeSubsets:
    success: list[URLScreenshotOutcome] = []
    failed: list[URLScreenshotOutcome] = []
    for outcome in outcomes:
        if outcome.success:
            success.append(outcome)
        else:
            failed.append(outcome)
    return URLScreenshotOutcomeSubsets(success=success, failed=failed)