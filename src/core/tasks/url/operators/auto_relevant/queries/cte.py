from sqlalchemy import select, CTE
from sqlalchemy.orm import aliased

from src.db.enums import TaskType
from src.db.helpers.query import not_exists_url, no_url_task_error
from src.db.models.impl.annotation.url_type.auto.sqlalchemy import AnnotationAutoURLType
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML


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
                not_exists_url(AnnotationAutoURLType),
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
