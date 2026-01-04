from src.db.models.impl.annotation.location.auto.suggestion.sqlalchemy import AnnotationLocationAutoSuggestion
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class LocationIDSubtaskSuggestionPydantic(BulkInsertableModel):

    subtask_id: int
    location_id: int
    confidence: float

    @classmethod
    def sa_model(cls) -> type[Base]:
        """Defines the SQLAlchemy model."""
        return AnnotationLocationAutoSuggestion