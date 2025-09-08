from pydantic import BaseModel


class SearchAgencyByLocationParams(BaseModel):
    request_id: int
    query: str