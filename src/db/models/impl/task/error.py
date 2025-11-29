from sqlalchemy import Column, Text, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from src.db.models.mixins import UpdatedAtMixin, TaskDependentMixin
from src.db.models.templates_.base import Base
from src.db.models.templates_.with_id import WithIDBase


class TaskError(UpdatedAtMixin, TaskDependentMixin, Base):
    __tablename__ = 'task_errors'

    error = Column(Text, nullable=False)

    # Relationships
    task = relationship("Task")

    __table_args__ = (PrimaryKeyConstraint(
        "task_id",
        "error",
    ),
    )
