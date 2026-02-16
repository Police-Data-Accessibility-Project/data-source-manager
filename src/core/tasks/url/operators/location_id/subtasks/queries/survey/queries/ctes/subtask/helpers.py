from sqlalchemy import ColumnElement, exists

from src.db.models.impl.annotation.location.auto.subtask.enums import LocationIDSubtaskType
from src.db.models.impl.annotation.location.auto.subtask.sqlalchemy import AnnotationLocationAutoSubtask
from src.db.models.impl.url.core.sqlalchemy import URL


def get_exists_subtask_query(
    subtask_type: LocationIDSubtaskType,
) -> ColumnElement[bool]:
    return (
        exists()
        .where(
            AnnotationLocationAutoSubtask.url_id == URL.id,
            AnnotationLocationAutoSubtask.type == subtask_type,
        )
        .label("subtask_entry_exists")
    )