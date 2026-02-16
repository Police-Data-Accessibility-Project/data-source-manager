from enum import Enum


class AgencyProposalRequestStatus(Enum):
    SUCCESS = "SUCCESS"
    PROPOSAL_DUPLICATE = "PROPOSAL_DUPLICATE"
    ACCEPTED_DUPLICATE = "ACCEPTED_DUPLICATE"
    ERROR = "ERROR"
