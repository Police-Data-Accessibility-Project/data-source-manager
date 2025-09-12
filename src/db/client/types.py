from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserRelevantSuggestion

UserSuggestionModel = UserRelevantSuggestion or UserRecordTypeSuggestion or UserUrlAgencySuggestion
