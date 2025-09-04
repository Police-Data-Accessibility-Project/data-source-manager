from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType, SubtaskDetailCode
from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLAutoAgencyIDSubtaskPydantic(BulkInsertableModel):
    task_id: int
    url_id: int
    subtask: AutoAgencyIDSubtaskType
    agencies_found: bool
    detail: SubtaskDetailCode = SubtaskDetailCode.NO_DETAILS

    @classmethod
    def sa_model(cls) -> type[Base]:
        return URLAutoAgencyIDSubtask