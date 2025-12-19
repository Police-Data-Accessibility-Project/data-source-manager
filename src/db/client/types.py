from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.record_type.user.user import AnnotationUserRecordType
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationUserURLType

UserSuggestionModel = AnnotationUserURLType or AnnotationUserRecordType or AnnotationAgencyUser
