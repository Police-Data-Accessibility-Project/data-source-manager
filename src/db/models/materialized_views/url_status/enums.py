from enum import Enum


class URLStatusViewEnum(Enum):
    INTAKE = "Intake"
    ACCEPTED = "Accepted"
    AWAITING_SUBMISSION = "Awaiting Submission"
    SUBMITTED = "Submitted"
    ERROR = "Error"
    COMMUNITY_LABELING = "Community Labeling"