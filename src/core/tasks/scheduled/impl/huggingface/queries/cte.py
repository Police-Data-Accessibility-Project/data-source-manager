from datetime import datetime

from sqlalchemy import select, Column

from src.db.enums import TaskType
from src.db.helpers.query import exists_url, no_url_task_error, not_exists_url
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.materialized_views.html_duplicate_url import HTMLDuplicateURLMaterializedView


class HuggingfacePrereqCTEContainer:

    def __init__(self):
        self.cte = (
            select(
                URL.id,
                URL.updated_at
            )
            .join(
                URLCompressedHTML,
                URL.id == URLCompressedHTML.url_id
            )
            .where(
                exists_url(FlagURLValidated),
                not_exists_url(HTMLDuplicateURLMaterializedView),
                no_url_task_error(TaskType.PUSH_TO_HUGGINGFACE)
            )
        )

    @property
    def url_id(self) -> Column[int]:
        return self.cte.c.id

    @property
    def updated_at(self) -> Column[datetime]:
        return self.cte.c.updated_at