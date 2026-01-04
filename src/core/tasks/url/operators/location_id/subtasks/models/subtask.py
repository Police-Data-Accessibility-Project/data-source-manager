from pydantic import BaseModel

from src.core.tasks.url.operators.location_id.subtasks.models.suggestion import LocationSuggestion
from src.db.models.impl.annotation.location.auto.subtask.pydantic import AutoLocationIDSubtaskPydantic


class AutoLocationIDSubtaskData(BaseModel):
    pydantic_model: AutoLocationIDSubtaskPydantic
    suggestions: list[LocationSuggestion]
    error: str | None = None

    @property
    def has_error(self) -> bool:
        return self.error is not None

    @property
    def url_id(self) -> int:
        return self.pydantic_model.url_id