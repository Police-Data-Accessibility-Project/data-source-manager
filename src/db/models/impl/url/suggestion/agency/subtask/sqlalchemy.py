from sqlalchemy.orm import relationship

from src.db.models.helpers import enum_column
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType, SubtaskDetailCode
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin, TaskDependentMixin
from src.db.models.templates_.with_id import WithIDBase

import sqlalchemy as sa

class URLAutoAgencyIDSubtask(
    WithIDBase,
    URLDependentMixin,
    TaskDependentMixin,
    CreatedAtMixin
):

    __tablename__ = "url_auto_agency_id_subtasks"

    subtask = enum_column(
        AutoAgencyIDSubtaskType,
        name="agency_auto_suggestion_method"
    )
    agencies_found = sa.Column(
        sa.Boolean(),
        nullable=False
    )
    detail = enum_column(
        SubtaskDetailCode,
        name="agency_id_subtask_detail_code",
    )

    suggestions = relationship(
        "AgencyIDSubtaskSuggestion",
        cascade="all, delete-orphan"
    )