from collections import Counter

from src.api.endpoints.annotate.all.get.models.record_type import RecordTypeAnnotationSuggestion
from src.api.endpoints.annotate.all.get.models.url_type import URLTypeAnnotationSuggestion
from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserURLTypeSuggestion


def convert_user_url_type_suggestion_to_url_type_annotation_suggestion(
    db_suggestions: list[UserURLTypeSuggestion]
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
    db_suggestions: list[UserRecordTypeSuggestion]
) -> list[RecordTypeAnnotationSuggestion]:
    counter: Counter[RecordType] = Counter()
    for suggestion in db_suggestions:
        counter[suggestion.record_type] += 1

    anno_suggestions: list[RecordTypeAnnotationSuggestion] = []
    for record_type, endorsement_count in counter.most_common(3):
        anno_suggestions.append(
            RecordTypeAnnotationSuggestion(
                record_type=record_type,
                endorsement_count=endorsement_count,
            )
        )

    return anno_suggestions