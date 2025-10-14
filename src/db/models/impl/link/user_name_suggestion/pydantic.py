from src.db.models.impl.link.user_name_suggestion.sqlalchemy import LinkUserNameSuggestion
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class LinkUserNameSuggestionPydantic(BulkInsertableModel):

    suggestion_id: int
    user_id: int

    @classmethod
    def sa_model(cls) -> type[LinkUserNameSuggestion]:
        return LinkUserNameSuggestion