"""Model for Internet Archive domain search results."""
from pydantic import BaseModel

from src.external.internet_archives.models.capture import IACapture


class IADomainSearchResult(BaseModel):
    """Result of searching the Internet Archive CDX API for a domain."""

    domain: str
    captures: list[IACapture]
    error: str | None = None
