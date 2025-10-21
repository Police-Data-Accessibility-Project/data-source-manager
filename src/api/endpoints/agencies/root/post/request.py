from src.api.shared.models.request_base import RequestBase
from src.db.models.impl.agency.enums import AgencyType, JurisdictionType


class AgencyPostRequest(RequestBase):
    name: str
    type: AgencyType
    jurisdiction_type: JurisdictionType
    location_ids: list[int]