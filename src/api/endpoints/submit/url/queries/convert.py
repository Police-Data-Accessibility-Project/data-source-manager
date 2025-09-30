from src.api.endpoints.submit.url.enums import URLSubmissionStatus
from src.api.endpoints.submit.url.models.response import URLSubmissionResponse


def convert_invalid_url_to_url_response(
    url: str
) -> URLSubmissionResponse:
    return URLSubmissionResponse(
        url_original=url,
        status=URLSubmissionStatus.INVALID,
    )

def convert_duplicate_urls_to_url_response(
    clean_url: str,
    original_url: str
) -> URLSubmissionResponse:
    return URLSubmissionResponse(
        url_original=original_url,
        url_cleaned=clean_url,
        status=URLSubmissionStatus.DATABASE_DUPLICATE,
    )
