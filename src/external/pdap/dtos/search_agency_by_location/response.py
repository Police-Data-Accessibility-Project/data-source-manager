from pydantic import BaseModel, Field

class SearchAgencyByLocationAgencyInfo(BaseModel):
    agency_id: int
    similarity: float = Field(ge=0, le=1)

class SearchAgencyByLocationResponse(BaseModel):
    request_id: int
    results: list[SearchAgencyByLocationAgencyInfo] = Field(min_length=1)

class SearchAgencyByLocationOuterResponse(BaseModel):
    responses: list[SearchAgencyByLocationResponse]