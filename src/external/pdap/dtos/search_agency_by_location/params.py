from pydantic import BaseModel, Field


class SearchAgencyByLocationParams(BaseModel):
    request_id: int
    query: str
    iso: str = Field(
        description="US State ISO Code",
        max_length=2,

    )