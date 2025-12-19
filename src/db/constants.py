from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.record_type.user.user import AnnotationUserRecordType
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationUserURLType

PLACEHOLDER_AGENCY_NAME = "PLACEHOLDER_AGENCY_NAME"

STANDARD_ROW_LIMIT = 100

USER_ANNOTATION_MODELS = [
    AnnotationUserURLType,
    AnnotationUserRecordType,
    AnnotationAgencyUser
]