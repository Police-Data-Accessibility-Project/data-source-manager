from pydantic import BaseModel, Field


class SearchSimilarLocationsLocationInfo(BaseModel):
    location_id: int
    similarity: float = Field(ge=0, le=1)

class SearchSimilarLocationsResponse(BaseModel):
    request_id: int
    results: list[SearchSimilarLocationsLocationInfo]

class SearchSimilarLocationsOuterResponse(BaseModel):
    responses: list[SearchSimilarLocationsResponse]