from sqlalchemy import Column, String

from src.db.models.helpers import enum_column
from src.db.models.impl.url.suggestion.location.auto.subtask.constants import MAX_SUGGESTION_LENGTH
from src.db.models.impl.url.suggestion.name.enums import NameSuggestionSource
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin
from src.db.models.templates_.with_id import WithIDBase


class URLNameSuggestion(
    WithIDBase,
    CreatedAtMixin,
    URLDependentMixin
):

    __tablename__ = "url_name_suggestions"

    suggestion = Column(String(MAX_SUGGESTION_LENGTH), nullable=False)
    source = enum_column(
        NameSuggestionSource,
        name="suggestion_source_enum"
    )