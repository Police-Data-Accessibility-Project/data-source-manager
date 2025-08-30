from pydantic import BaseModel


class AgencyURLMappings(BaseModel):
    agency_id: int
    url_ids: list[int]