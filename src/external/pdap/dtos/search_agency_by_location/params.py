from pydantic import BaseModel


class SearchAgencyByLocationParams(BaseModel):
    request_id: int
    state_iso: str | None
    locations: list[str]