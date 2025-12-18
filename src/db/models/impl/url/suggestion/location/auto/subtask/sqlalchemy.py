from sqlalchemy import Column, Boolean
from sqlalchemy.orm import relationship, Mapped

from src.db.models.helpers import enum_column
from src.db.models.impl.url.suggestion.location.auto.subtask.enums import LocationIDSubtaskType
from src.db.models.impl.url.suggestion.location.auto.suggestion.sqlalchemy import LocationIDSubtaskSuggestion
from src.db.models.mixins import CreatedAtMixin, TaskDependentMixin, URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class AutoLocationIDSubtask(
    WithIDBase,
    CreatedAtMixin,
    TaskDependentMixin,
    URLDependentMixin,
):

    __tablename__ = 'annotation__auto__location__subtasks'

    locations_found = Column(Boolean(), nullable=False)
    type: Mapped[LocationIDSubtaskType] = enum_column(
        LocationIDSubtaskType,
        name='auto_location_id_subtask_type'
    )

    suggestions = relationship(
        LocationIDSubtaskSuggestion
    )