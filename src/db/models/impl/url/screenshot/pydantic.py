from src.db.models.impl.url.screenshot.sqlalchemy import URLScreenshot
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLScreenshotPydantic(BulkInsertableModel):
    url_id: int
    content: bytes
    file_size: int

    @classmethod
    def sa_model(cls) -> type[Base]:
        return URLScreenshot
