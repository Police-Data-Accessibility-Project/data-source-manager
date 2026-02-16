from pydantic import BaseModel


class ProposalAgencyRejectResponse(BaseModel):
    success: bool
    message: str