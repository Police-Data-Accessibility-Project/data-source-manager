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

def remove_url_scheme(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme:
        return url.replace(f"{parsed.scheme}://", "", 1)
    return url


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        # If scheme is missing, `netloc` will be empty, so we check path too
        if result.scheme in ("http", "https") and result.netloc:
            return True
        if not result.scheme and result.path:
            # no scheme, treat path as potential domain
            return "." in result.path
        return False
    except ValueError:
        return False
