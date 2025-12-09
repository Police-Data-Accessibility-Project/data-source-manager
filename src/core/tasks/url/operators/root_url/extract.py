from urllib.parse import urlparse, ParseResult


def extract_root_url(url: str) -> str:
    # URLs in DB should not have HTTPS -- add to enable url parse to function properly
    parsed_url: ParseResult = urlparse(f"https://{url}")
    root_url = parsed_url.netloc
    return root_url.rstrip("/")