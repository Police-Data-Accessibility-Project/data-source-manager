from sqlalchemy import select, exists, CTE, Column

from src.db.enums import URLHTMLContentType, TaskType
from src.db.helpers.query import no_url_task_error
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.html.content.sqlalchemy import URLHTMLContent
from src.db.models.impl.url.suggestion.name.enums import NameSuggestionSource
from src.db.models.impl.url.suggestion.name.sqlalchemy import URLNameSuggestion


class AutoNamePrerequisiteCTEContainer:

    def __init__(self):
        self._query = (
            select(
                URL.id.label("url_id"),
                URLHTMLContent.content
            )
            .join(
                URLHTMLContent,
                URLHTMLContent.url_id == URL.id
            )
            .where(
                URLHTMLContent.content_type == URLHTMLContentType.TITLE.value,
                ~exists(
                    select(
                        URLNameSuggestion.id
                    )
                    .where(
                        URLNameSuggestion.url_id == URL.id,
                        URLNameSuggestion.source == NameSuggestionSource.HTML_METADATA_TITLE.value,
                    )
                ),
                no_url_task_error(TaskType.AUTO_NAME)
            ).cte("auto_name_prerequisites")
        )

    @property
    def cte(self) -> CTE:
        return self._query

    @property
    def url_id(self) -> Column[int]:
        return self.cte.c.url_id

    @property
    def content(self) -> Column[str]:
        return self.cte.c.content