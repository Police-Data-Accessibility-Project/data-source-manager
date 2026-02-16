from pydantic import BaseModel

from src.core.tasks.url.operators.agency_identification.subtasks.models.suggestion import AgencySuggestion
from src.db.models.impl.annotation.agency.auto.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic


class AutoAgencyIDSubtaskData(BaseModel):
    pydantic_model: URLAutoAgencyIDSubtaskPydantic
    suggestions: list[AgencySuggestion]
    error: str | None = None

    @property
    def has_error(self) -> bool:
        return self.error is not None

    @property
    def url_id(self) -> int:
        return self.pydantic_model.url_id