from sqlalchemy import select, CTE, Column

from src.db.enums import TaskType
from src.db.helpers.query import not_exists_url, no_url_task_error
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.suggestion.record_type.auto import AutoRecordTypeSuggestion


class RecordTypeTaskPrerequisiteCTEContainer:

    def __init__(self):
        self.cte: CTE = (
            select(
                URL.id
            )
            .join(
                URLCompressedHTML
            )
            .where(
                not_exists_url(AutoRecordTypeSuggestion),
                no_url_task_error(
                    TaskType.RECORD_TYPE
                )
            )
            .cte("record_type_task_prerequisite")
        )

    @property
    def url_id(self) -> Column[int]:
        return self.cte.columns.id