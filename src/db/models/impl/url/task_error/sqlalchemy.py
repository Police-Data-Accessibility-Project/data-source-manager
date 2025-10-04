from sqlalchemy import String, Column, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.db.enums import TaskType
from src.db.models.helpers import enum_column
from src.db.models.mixins import URLDependentMixin, TaskDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class URLTaskError(
    Base,
    URLDependentMixin,
    TaskDependentMixin,
    CreatedAtMixin,
):
    __tablename__ = "url_task_error"

    task_type: Mapped[TaskType] = enum_column(TaskType, name="task_type")
    error: Mapped[str] = Column(String)

    __table_args__ = (
        PrimaryKeyConstraint("url_id", "task_type"),
    )