from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped

from src.db.models.helpers import enum_column
from src.db.models.impl.annotation.location.auto.subtask.constants import MAX_SUGGESTION_LENGTH
from src.db.models.impl.annotation.name.suggestion.enums import NameSuggestionSource
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin
from src.db.models.templates_.with_id import WithIDBase


class AnnotationNameSuggestion(
    WithIDBase,
    CreatedAtMixin,
    URLDependentMixin
):

    __tablename__ = "annotation__name__suggestions"

    suggestion = Column(String(MAX_SUGGESTION_LENGTH), nullable=False)
    source: Mapped[NameSuggestionSource] = enum_column(
        NameSuggestionSource,
        name="suggestion_source_enum"
    )