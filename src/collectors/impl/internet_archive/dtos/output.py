from pydantic import BaseModel


class InternetArchiveURLResult(BaseModel):
    url: str
    archive_url: str
    timestamp: int
    digest: str


class InternetArchiveOutputDTO(BaseModel):
    domain: str
    urls: list[InternetArchiveURLResult]
