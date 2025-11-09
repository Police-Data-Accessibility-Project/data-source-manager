from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.impl.url.suggestion.agency.user import UserURLAgencySuggestion
from src.db.models.impl.url.suggestion.record_type.auto import AutoRecordTypeSuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.relevant.auto.sqlalchemy import AutoRelevantSuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserURLTypeSuggestion

ALL_ANNOTATION_MODELS = [
    AutoRecordTypeSuggestion,
    AutoRelevantSuggestion,
    URLAutoAgencyIDSubtask,
    UserURLTypeSuggestion,
    UserRecordTypeSuggestion,
    UserURLAgencySuggestion
]
