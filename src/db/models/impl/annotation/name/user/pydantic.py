from src.db.models.impl.annotation.name.user.sqlalchemy import AnnotationNameUserEndorsement
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class LinkUserNameSuggestionPydantic(BulkInsertableModel):

    suggestion_id: int
    user_id: int

    @classmethod
    def sa_model(cls) -> type[AnnotationNameUserEndorsement]:
        return AnnotationNameUserEndorsement