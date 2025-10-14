from sqlalchemy import CTE, select, Column

from src.db.enums import TaskType
from src.db.helpers.query import url_not_validated, not_exists_url, no_url_task_error
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.screenshot.sqlalchemy import URLScreenshot
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata


class URLScreenshotPrerequisitesCTEContainer:

    def __init__(self):
        self._cte: CTE = (
            select(
                URL.id.label("url_id"),
                URL.url,
            )
            .join(
                URLWebMetadata,
                URL.id == URLWebMetadata.url_id
            )
            .where(
                url_not_validated(),
                not_exists_url(URLScreenshot),
                no_url_task_error(TaskType.SCREENSHOT),
                URLWebMetadata.status_code == 200,
            )
            .cte("url_screenshot_prerequisites")
        )

    @property
    def url_id(self) -> Column[int]:
        return self._cte.c.url_id

    @property
    def url(self) -> Column[str]:
        return self._cte.c.url