from src.db.models.impl.url.suggestion.agency.user import UserURLAgencySuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserURLTypeSuggestion

UserSuggestionModel = UserURLTypeSuggestion or UserRecordTypeSuggestion or UserURLAgencySuggestion
