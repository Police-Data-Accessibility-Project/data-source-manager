from pydantic import BaseModel

from src.db.models.impl.agency.enums import AgencyType, JurisdictionType


class AgencyPostRequest(BaseModel):
    name: str
    type: AgencyType
    jurisdiction_type: JurisdictionType
    location_ids: list[int]