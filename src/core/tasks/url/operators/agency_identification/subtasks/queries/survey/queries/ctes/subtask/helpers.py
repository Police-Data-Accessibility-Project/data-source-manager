from sqlalchemy import ColumnElement, exists

from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.annotation.agency.auto.subtask.sqlalchemy import AnnotationAgencyAutoSubtask
from src.db.models.impl.url.core.sqlalchemy import URL


def get_exists_subtask_query(
    subtask_type: AutoAgencyIDSubtaskType,
) -> ColumnElement[bool]:
    return (
        exists()
        .where(
            AnnotationAgencyAutoSubtask.url_id == URL.id,
            AnnotationAgencyAutoSubtask.type == subtask_type,
        )
        .label("subtask_entry_exists")
    )