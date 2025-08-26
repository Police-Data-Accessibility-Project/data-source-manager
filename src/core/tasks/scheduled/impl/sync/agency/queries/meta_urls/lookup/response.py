from pydantic import BaseModel

from src.db.dtos.url.mapping import URLMapping


class AgencyMetaURLLookupResponse(BaseModel):
    agency_id: int
    exists_in_db: bool
    url_mappings: list[URLMapping] = []
