from pydantic import BaseModel


class ProposalAgencyApproveResponse(BaseModel):
    message: str
    success: bool
    agency_id: int | None = None