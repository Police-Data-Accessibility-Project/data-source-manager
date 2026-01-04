from pydantic import BaseModel

from src.api.endpoints.agencies.by_id.locations.get.response import AgencyGetLocationsResponse


class ProposalAgencyGetLocationsOuterResponse(BaseModel):
    results: list[AgencyGetLocationsResponse]