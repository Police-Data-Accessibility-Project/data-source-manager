from typing import TypeVar

from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.record_type.user.user import AnnotationRecordTypeUser
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationURLTypeUser
from src.db.queries.base.labels import LabelsBase

UserSuggestionType = AnnotationAgencyUser | AnnotationURLTypeUser | AnnotationRecordTypeUser

LabelsType = TypeVar("LabelsType", bound=LabelsBase)