from pydantic import BaseModel

from src.db.enums import TaskType
from src.db.models.impl.url.task_error.sqlalchemy import URLTaskError
from src.db.models.templates_.base import Base


class URLTaskErrorPydantic(BaseModel):

    url_id: int
    task_id: int
    task_type: TaskType
    error: str

    @classmethod
    def sa_model(cls) -> type[Base]:
        """Defines the SQLAlchemy model."""
        return URLTaskError
