from pydantic import BaseModel

class AgencyMetaURLLookupResponse(BaseModel):
    url: str
    url_id: int | None
    agency_ids: list[int] = []

    @property
    def exists_in_db(self) -> bool:
        return self.url_id is not None