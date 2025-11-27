from enum import Enum


class ApprovalStatus(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    NEEDS_IDENTIFICATION = "needs identification"

class DataSourcesURLStatus(Enum):
    AVAILABLE = "available"
    BROKEN = "broken"
    OK = "ok"
    NONE_FOUND = "none found"