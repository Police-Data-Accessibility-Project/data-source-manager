from src.db.models.impl.url.suggestion.agency.suggestion.sqlalchemy import AgencyIDSubtaskSuggestion
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class AgencyIDSubtaskSuggestionPydantic(
    BulkInsertableModel,
):
    subtask_id: int
    agency_id: int
    confidence: int

    @classmethod
    def sa_model(cls) -> type[Base]:
        """Defines the SQLAlchemy model."""
        return AgencyIDSubtaskSuggestion