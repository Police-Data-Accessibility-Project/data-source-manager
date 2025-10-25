from pydantic import BaseModel


class MetaURLGetResponse(BaseModel):
    url_id: int
    url: str

    # Required Attributes
    name: str
    agency_ids: list[int]

    # Optional Attributes
    batch_id: int| None
    description: str | None

class MetaURLGetOuterResponse(BaseModel):
    results: list[MetaURLGetResponse]