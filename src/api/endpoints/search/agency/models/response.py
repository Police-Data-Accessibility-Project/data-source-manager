from pydantic import BaseModel


class AgencySearchResponse(BaseModel):
    agency_id: int
    agency_name: str
    location_display_name: str
