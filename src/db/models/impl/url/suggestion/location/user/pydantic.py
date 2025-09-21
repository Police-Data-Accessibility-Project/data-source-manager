from src.db.models.impl.url.suggestion.location.user.sqlalchemy import UserLocationSuggestion
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class UserLocationSuggestionPydantic(
    BulkInsertableModel,
):

    location_id: int
    url_id: int

    @classmethod
    def sa_model(cls) -> type[Base]:
        """Defines the SQLAlchemy model."""
        return UserLocationSuggestion
