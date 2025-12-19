from src.db.models.impl.annotation.agency.auto.subtask.sqlalchemy import AnnotationAgencyAutoSubtask
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.record_type.auto.sqlalchemy import AnnotationAutoRecordType
from src.db.models.impl.annotation.record_type.user.user import AnnotationUserRecordType
from src.db.models.impl.annotation.url_type.auto.sqlalchemy import AnnotationAutoURLType
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationUserURLType

ALL_ANNOTATION_MODELS = [
    AnnotationAutoRecordType,
    AnnotationAutoURLType,
    AnnotationAgencyAutoSubtask,
    AnnotationUserURLType,
    AnnotationUserRecordType,
    AnnotationAgencyUser
]
