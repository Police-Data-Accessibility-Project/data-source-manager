from pydantic import Field

from src.db.models.impl.annotation.location.auto.subtask.constants import MAX_SUGGESTION_LENGTH
from src.db.models.impl.annotation.name.suggestion.enums import NameSuggestionSource
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLNameSuggestionPydantic(BulkInsertableModel):

    url_id: int
    suggestion: str = Field(..., max_length=MAX_SUGGESTION_LENGTH)
    source: NameSuggestionSource

    @classmethod
    def sa_model(cls) -> type[AnnotationNameSuggestion]:
        return AnnotationNameSuggestion