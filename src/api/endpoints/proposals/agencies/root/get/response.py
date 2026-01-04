from datetime import datetime

from pydantic import BaseModel

from src.api.endpoints.agencies.by_id.locations.get.response import AgencyGetLocationsResponse
from src.db.models.impl.agency.enums import AgencyType, JurisdictionType

class ProposalAgencyGetResponse(BaseModel):
    id: int
    name: str
    proposing_user_id: int | None
    agency_type: AgencyType
    jurisdiction_type: JurisdictionType
    locations: list[AgencyGetLocationsResponse]
    created_at: datetime

class ProposalAgencyGetOuterResponse(BaseModel):
    results: list[ProposalAgencyGetResponse]