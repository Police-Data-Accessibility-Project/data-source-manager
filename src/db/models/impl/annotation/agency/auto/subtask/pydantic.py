from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType, SubtaskDetailCode
from src.db.models.impl.annotation.agency.auto.subtask.sqlalchemy import AnnotationAgencyAutoSubtask
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel

type_alias = type

class URLAutoAgencyIDSubtaskPydantic(BulkInsertableModel):
    task_id: int
    url_id: int
    type: AutoAgencyIDSubtaskType
    agencies_found: bool
    detail: SubtaskDetailCode = SubtaskDetailCode.NO_DETAILS

    @classmethod
    def sa_model(cls) -> type_alias[Base]:
        return AnnotationAgencyAutoSubtask