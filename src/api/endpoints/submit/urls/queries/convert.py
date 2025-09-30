from src.api.endpoints.submit.urls.enums import URLSubmissionStatus
from src.api.endpoints.submit.urls.models.response import URLSubmissionResponse


def convert_invalid_urls_to_url_response(
    urls: list[str]
) -> list[URLSubmissionResponse]:
    return [
        URLSubmissionResponse(
            url_original=url,
            status=URLSubmissionStatus.INVALID,
        )
        for url in urls
    ]

def convert_duplicate_urls_to_url_response(
    clean_urls: list[str],
    url_clean_original_mapping: dict[str, str]
) -> list[URLSubmissionResponse]:
    raise NotImplementedError