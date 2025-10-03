from pydantic import BaseModel


class SubmitMetaURLsRequest(BaseModel):
    url_id: int
    url: str
    agency_id: int
