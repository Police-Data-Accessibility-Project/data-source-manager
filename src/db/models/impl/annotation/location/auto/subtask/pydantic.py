from src.db.models.impl.annotation.location.auto.subtask.enums import LocationIDSubtaskType
from src.db.models.impl.annotation.location.auto.subtask.sqlalchemy import AnnotationLocationAutoSubtask
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class AutoLocationIDSubtaskPydantic(
    BulkInsertableModel,
):

    url_id: int
    task_id: int
    locations_found: bool
    type: LocationIDSubtaskType

    @classmethod
    def sa_model(cls) -> type[Base]:
        """Defines the SQLAlchemy model."""
        return AnnotationLocationAutoSubtask