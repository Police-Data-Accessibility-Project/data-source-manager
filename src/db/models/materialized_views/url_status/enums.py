"""

ASE status_text.status
        WHEN 'Intake'::text THEN 100
        WHEN 'Error'::text THEN 110
        WHEN 'Community Labeling'::text THEN 200
        WHEN 'Accepted'::text THEN 300
        WHEN 'Awaiting Submission'::text THEN 380
        WHEN 'Submitted'::text THEN 390
"""
from sqlalchemy import Enum


class URLStatusEnum(Enum):
    INTAKE = "Intake"
    ERROR = "Error"
    COMMUNITY_LABELING = "Community Labeling"
    ACCEPTED = "Accepted"
    AWAITING_SUBMISSION = "Awaiting Submission"
    SUBMITTED = "Submitted"