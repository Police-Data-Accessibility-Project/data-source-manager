from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtask
from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLAutoAgencyIDSubtaskPydantic(BulkInsertableModel):
    url_id: int
    subtask: AutoAgencyIDSubtask
    agencies_found: bool
    auto_comment: str | None = None

    @classmethod
    def sa_model(cls) -> type[Base]:
        return URLAutoAgencyIDSubtask