from sqlalchemy import CTE, select, exists, Column

from src.db.helpers.query import url_not_validated, not_exists_url
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.error.url_screenshot.sqlalchemy import ErrorURLScreenshot
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
                not_exists_url(ErrorURLScreenshot),
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