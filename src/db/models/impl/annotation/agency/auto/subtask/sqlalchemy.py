from sqlalchemy.orm import relationship, Mapped

from src.db.models.helpers import enum_column
from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType, SubtaskDetailCode
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin, TaskDependentMixin
from src.db.models.templates_.with_id import WithIDBase

import sqlalchemy as sa

class AnnotationAgencyAutoSubtask(
    WithIDBase,
    URLDependentMixin,
    TaskDependentMixin,
    CreatedAtMixin
):

    __tablename__ = "annotation__agency__auto__subtasks"

    type: Mapped[AutoAgencyIDSubtaskType] = enum_column(
        AutoAgencyIDSubtaskType,
        name="agency_auto_suggestion_method"
    )
    agencies_found = sa.Column(
        sa.Boolean(),
        nullable=False
    )
    detail: Mapped[SubtaskDetailCode] = enum_column(
        SubtaskDetailCode,
        name="agency_id_subtask_detail_code",
    )

    suggestions = relationship(
        "AnnotationAgencyAutoSuggestion",
        cascade="all, delete-orphan"
    )