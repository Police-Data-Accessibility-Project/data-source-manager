from urllib.parse import urlparse

from src.util.models.url_and_scheme import URLAndScheme


def clean_url(url: str) -> str:
    # Remove Non-breaking spaces
    url = url.strip(" ")

    # Remove any fragments and everything after them
    url = url.split("#")[0]
    return url

def get_url_and_scheme(
    url: str
) -> URLAndScheme:
    parsed = urlparse(url)
    if parsed.scheme:
        remainder = url.replace(f"{parsed.scheme}://", "", 1)
        return URLAndScheme(
            url=remainder,
            scheme=parsed.scheme
        )
    # Handle URLs without scheme
    return URLAndScheme(
        url=url,
        scheme=None
    )
