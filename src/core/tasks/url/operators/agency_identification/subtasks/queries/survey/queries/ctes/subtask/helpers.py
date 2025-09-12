from sqlalchemy import ColumnElement, exists

from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask


def get_exists_subtask_query(
    subtask_type: AutoAgencyIDSubtaskType,
) -> ColumnElement[bool]:
    return (
        exists()
        .where(
            URLAutoAgencyIDSubtask.url_id == URL.id,
            URLAutoAgencyIDSubtask.type == subtask_type,
        )
        .label("subtask_entry_exists")
    )