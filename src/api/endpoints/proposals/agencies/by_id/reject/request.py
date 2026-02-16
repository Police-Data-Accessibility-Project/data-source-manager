from pydantic import BaseModel


class ProposalAgencyRejectRequestModel(BaseModel):
    rejection_reason: str