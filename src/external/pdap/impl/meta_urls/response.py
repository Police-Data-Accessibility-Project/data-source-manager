from pydantic import BaseModel

from src.external.pdap.impl.meta_urls.enums import SubmitMetaURLsStatus


class SubmitMetaURLsResponse(BaseModel):
    url: str
    status: SubmitMetaURLsStatus
    meta_url_id: int | None = None
    agency_id: int | None = None
    error: str | None = None