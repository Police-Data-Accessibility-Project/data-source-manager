from pydantic import BaseModel

from src.api.endpoints.agencies.by_id.locations.get.response import AgencyGetLocationsResponse
from src.db.models.impl.agency.enums import AgencyType, JurisdictionType


class AgencyGetResponse(BaseModel):
    id: int
    name: str
    type: AgencyType
    jurisdiction_type: JurisdictionType
    locations: list[AgencyGetLocationsResponse]