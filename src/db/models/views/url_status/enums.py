from enum import Enum


class URLStatusViewEnum(Enum):
    INTAKE = "Intake"
    ACCEPTED = "Accepted"
    SUBMITTED_PIPELINE_COMPLETE = "Submitted/Pipeline Complete"
    ERROR = "Error"
    COMMUNITY_LABELING = "Community Labeling"