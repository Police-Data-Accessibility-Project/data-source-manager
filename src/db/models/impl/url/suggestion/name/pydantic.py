from pydantic import Field

from src.db.models.impl.url.suggestion.location.auto.subtask.constants import MAX_SUGGESTION_LENGTH
from src.db.models.impl.url.suggestion.name.enums import NameSuggestionSource
from src.db.models.impl.url.suggestion.name.sqlalchemy import URLNameSuggestion
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLNameSuggestionPydantic(BulkInsertableModel):

    url_id: int
    suggestion: str = Field(..., max_length=MAX_SUGGESTION_LENGTH)
    source: NameSuggestionSource

    @classmethod
    def sa_model(cls) -> type[URLNameSuggestion]:
        return URLNameSuggestion