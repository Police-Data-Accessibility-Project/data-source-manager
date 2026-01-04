from src.db.models.impl.annotation.agency.auto.subtask.sqlalchemy import AnnotationAgencyAutoSubtask
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.record_type.auto.sqlalchemy import AnnotationAutoRecordType
from src.db.models.impl.annotation.record_type.user.user import AnnotationRecordTypeUser
from src.db.models.impl.annotation.url_type.auto.sqlalchemy import AnnotationAutoURLType
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationURLTypeUser

ALL_ANNOTATION_MODELS = [
    AnnotationAutoRecordType,
    AnnotationAutoURLType,
    AnnotationAgencyAutoSubtask,
    AnnotationURLTypeUser,
    AnnotationRecordTypeUser,
    AnnotationAgencyUser
]
