from pydantic import BaseModel


class GetAgenciesLinkedToAnnotatedLocationsResponse(BaseModel):
    url_id: int
    location_id: int
    location_confidence: int
    agency_ids: list[int]