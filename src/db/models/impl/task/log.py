from sqlalchemy import Column, Text, PrimaryKeyConstraint

from src.db.models.mixins import TaskDependentMixin, UpdatedAtMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class TaskLog(
    Base,
    TaskDependentMixin,
    CreatedAtMixin,
):
    __tablename__ = "tasks__log"
    __table_args__ = (
        PrimaryKeyConstraint("task_id"),
    )

    log = Column(Text, nullable=False)
