from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.record_type.user.user import AnnotationRecordTypeUser
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationURLTypeUser

PLACEHOLDER_AGENCY_NAME = "PLACEHOLDER_AGENCY_NAME"

STANDARD_ROW_LIMIT = 100

USER_ANNOTATION_MODELS = [
    AnnotationURLTypeUser,
    AnnotationRecordTypeUser,
    AnnotationAgencyUser
]