from pydantic import BaseModel


class AgencyGetLocationsResponse(BaseModel):
    location_id: int
    full_display_name: str
