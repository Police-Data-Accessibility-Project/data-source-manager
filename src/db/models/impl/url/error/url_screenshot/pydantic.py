from pydantic import BaseModel

from src.db.models.impl.url.error.url_screenshot.sqlalchemy import ErrorURLScreenshot
from src.db.models.templates_.base import Base


class ErrorURLScreenshotPydantic(BaseModel):
    url_id: int
    error: str

    @classmethod
    def sa_model(cls) -> type[Base]:
        return ErrorURLScreenshot