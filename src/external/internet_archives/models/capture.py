"""Model for an Internet Archive CDX capture record."""
from pydantic import BaseModel


class IACapture(BaseModel):
    """A single capture record from the Internet Archive CDX API."""

    timestamp: int
    original: str
    length: int
    digest: str
    mimetype: str | None = None
