from src.db.models.impl.url.suggestion.agency.user import UserURLAgencySuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.url_type.user import UserURLTypeSuggestion

PLACEHOLDER_AGENCY_NAME = "PLACEHOLDER_AGENCY_NAME"

STANDARD_ROW_LIMIT = 100

USER_ANNOTATION_MODELS = [
    UserURLTypeSuggestion,
    UserRecordTypeSuggestion,
    UserURLAgencySuggestion
]