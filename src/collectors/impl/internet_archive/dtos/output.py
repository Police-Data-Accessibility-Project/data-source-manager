"""Output DTOs for the Internet Archive collector."""
from pydantic import BaseModel


class InternetArchiveURLResult(BaseModel):
    """A single URL result from the Internet Archive."""

    url: str
    archive_url: str
    timestamp: int
    digest: str


class InternetArchiveOutputDTO(BaseModel):
    """Results for a single domain from the Internet Archive."""

    domain: str
    urls: list[InternetArchiveURLResult]
