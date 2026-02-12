from pydantic import BaseModel

from src.external.internet_archives.models.capture import IACapture


class IADomainSearchResult(BaseModel):
    domain: str
    captures: list[IACapture]
    error: str | None = None
