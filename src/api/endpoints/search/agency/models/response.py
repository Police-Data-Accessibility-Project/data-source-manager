from pydantic import BaseModel

from src.db.models.impl.agency.enums import AgencyType, JurisdictionType


class AgencySearchResponse(BaseModel):
    agency_id: int
    agency_name: str
    jurisdiction_type: JurisdictionType | None
    agency_type: AgencyType
    location_display_name: str
