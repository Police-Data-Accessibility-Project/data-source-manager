from pydantic import BaseModel

from src.db.models.impl.agency.enums import AgencyType, JurisdictionType


class SubmitAgencyRequestModel(BaseModel):
    name: str
    agency_type: AgencyType
    jurisdiction_type: JurisdictionType

    location_ids: list[int]