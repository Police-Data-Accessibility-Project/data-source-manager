from pydantic import BaseModel

from src.db.dtos.url.mapping import URLMapping


class AgencyMetaURLLookupResponse(BaseModel):
    agency_id: int
    exists_in_db: bool
    url_mappings: list[URLMapping] = []

    @property
    def meta_urls(self) -> list[str]:
        return [url_mapping.url for url_mapping in self.url_mappings]
