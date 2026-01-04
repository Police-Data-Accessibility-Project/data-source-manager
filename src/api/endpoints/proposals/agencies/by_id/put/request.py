from src.api.shared.models.request_base import RequestBase
from src.db.models.impl.agency.enums import AgencyType, JurisdictionType


class ProposalAgencyPutRequest(RequestBase):
    name: str | None = None
    type: AgencyType | None = None
    jurisdiction_type: JurisdictionType | None = None


