from sqlalchemy import select, CTE
from sqlalchemy.orm import aliased

from src.collectors.enums import URLStatus
from src.db.enums import TaskType
from src.db.helpers.query import not_exists_url, no_url_task_error
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.suggestion.url_type.auto.sqlalchemy import AutoRelevantSuggestion


class AutoRelevantPrerequisitesCTEContainer:

    def __init__(self):
        self._cte = (
            select(
                URL
            )
            .join(
                URLCompressedHTML,
                URL.id == URLCompressedHTML.url_id
            )
            .where(
                URL.status == URLStatus.OK.value,
                not_exists_url(AutoRelevantSuggestion),
                no_url_task_error(TaskType.RELEVANCY)
            ).cte("auto_relevant_prerequisites")
        )

        self._url_alias = aliased(URL, self._cte)

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def url_alias(self):
        """Return an ORM alias of URL mapped to the CTE."""
        return self._url_alias
