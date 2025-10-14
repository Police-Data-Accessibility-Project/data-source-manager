from pydantic import BaseModel, Field


class SearchSimilarLocationsParams(BaseModel):
    request_id: int
    query: str
    iso: str = Field(
        description="US State ISO Code",
        max_length=2,
    )