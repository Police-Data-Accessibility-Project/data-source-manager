from typing import TypeVar

from src.db.models.impl.url.suggestion.agency.user import UserURLAgencySuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserURLTypeSuggestion
from src.db.queries.base.labels import LabelsBase

UserSuggestionType = UserURLAgencySuggestion | UserURLTypeSuggestion | UserRecordTypeSuggestion

LabelsType = TypeVar("LabelsType", bound=LabelsBase)