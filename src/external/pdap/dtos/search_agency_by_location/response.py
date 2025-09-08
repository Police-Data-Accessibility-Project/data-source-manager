from pydantic import BaseModel, Field

class SearchAgencyByLocationResponse(BaseModel):
    request_id: int
    agency_id: int
    similarity: float = Field(ge=0, le=1)