from sqlalchemy import ColumnElement, exists

from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.location.auto.subtask.enums import LocationIDSubtaskType
from src.db.models.impl.url.suggestion.location.auto.subtask.sqlalchemy import AutoLocationIDSubtask


def get_exists_subtask_query(
    subtask_type: LocationIDSubtaskType,
) -> ColumnElement[bool]:
    return (
        exists()
        .where(
            AutoLocationIDSubtask.url_id == URL.id,
            AutoLocationIDSubtask.type == subtask_type,
        )
        .label("subtask_entry_exists")
    )