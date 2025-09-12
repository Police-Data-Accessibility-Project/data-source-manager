from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserRelevantSuggestion

PLACEHOLDER_AGENCY_NAME = "PLACEHOLDER_AGENCY_NAME"

STANDARD_ROW_LIMIT = 100

USER_ANNOTATION_MODELS = [
    UserRelevantSuggestion,
    UserRecordTypeSuggestion,
    UserUrlAgencySuggestion
]