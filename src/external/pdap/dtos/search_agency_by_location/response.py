from pydantic import BaseModel, Field


class SearchAgencyByLocationResult(BaseModel):
    agency_id: int
    similarity: float = Field(ge=0, le=1)

class SearchAgencyByLocationResponse(BaseModel):
    request_id: int
    results: list[SearchAgencyByLocationResult]