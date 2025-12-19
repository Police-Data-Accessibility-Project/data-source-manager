from collections import Counter

from src.api.endpoints.annotate.all.get.models.record_type import RecordTypeAnnotationResponseOuterInfo, \
    RecordTypeSuggestionModel
from src.api.endpoints.annotate.all.get.models.url_type import URLTypeAnnotationSuggestion
from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.annotation.record_type.user.user import AnnotationUserRecordType
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationUserURLType


def convert_user_url_type_suggestion_to_url_type_annotation_suggestion(
    db_suggestions: list[AnnotationUserURLType]
) -> list[URLTypeAnnotationSuggestion]:
    counter: Counter[URLType] = Counter()
    for suggestion in db_suggestions:
        counter[suggestion.type] += 1
    anno_suggestions: list[URLTypeAnnotationSuggestion] = []
    for url_type, endorsement_count in counter.most_common(3):
        anno_suggestions.append(
            URLTypeAnnotationSuggestion(
                url_type=url_type,
                endorsement_count=endorsement_count,
            )
        )
    return anno_suggestions

def convert_user_record_type_suggestion_to_record_type_annotation_suggestion(
    db_suggestions: list[AnnotationUserRecordType]
) -> RecordTypeAnnotationResponseOuterInfo:
    counter: Counter[RecordType] = Counter()
    for suggestion in db_suggestions:
        counter[suggestion.record_type] += 1

    suggestions: list[RecordTypeSuggestionModel] = []
    for record_type, endorsement_count in counter.most_common(3):
        suggestions.append(
            RecordTypeSuggestionModel(
                record_type=record_type,
                user_count=endorsement_count,
                robo_confidence=0,
            )
        )
    return RecordTypeAnnotationResponseOuterInfo(
        suggestions=suggestions
    )
