from pydantic import BaseModel

from src.api.endpoints.submit.agency.enums import AgencyProposalRequestStatus


class SubmitAgencyProposalResponse(BaseModel):
    proposal_id: int | None = None
    status: AgencyProposalRequestStatus
    details: str | None