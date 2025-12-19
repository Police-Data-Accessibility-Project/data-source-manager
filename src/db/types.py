from typing import TypeVar

from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.record_type.user.user import AnnotationUserRecordType
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationUserURLType
from src.db.queries.base.labels import LabelsBase

UserSuggestionType = AnnotationAgencyUser | AnnotationUserURLType | AnnotationUserRecordType

LabelsType = TypeVar("LabelsType", bound=LabelsBase)