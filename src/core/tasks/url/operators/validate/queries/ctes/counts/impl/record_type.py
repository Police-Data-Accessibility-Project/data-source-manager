from sqlalchemy import select, func

from src.core.tasks.url.operators.validate.queries.ctes.counts.constants import ANONYMOUS_VOTE_RATIO
from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer
from src.db.models.impl.url.suggestion.anonymous.record_type.sqlalchemy import AnonymousAnnotationRecordType
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.views.unvalidated_url import UnvalidatedURL

_user_counts = (
    select(
        UserRecordTypeSuggestion.url_id,
        UserRecordTypeSuggestion.record_type.label("entity"),
        func.count().label("votes")
    )
    .group_by(
        UserRecordTypeSuggestion.url_id,
        UserRecordTypeSuggestion.record_type
    )
)

_anon_counts = (
    select(
        AnonymousAnnotationRecordType.url_id,
        AnonymousAnnotationRecordType.record_type.label("entity"),
        (func.count() * ANONYMOUS_VOTE_RATIO).label("votes")
    )
    .group_by(
        AnonymousAnnotationRecordType.url_id,
        AnonymousAnnotationRecordType.record_type
    )
)

_union_counts = (
    select(
        _user_counts.c.url_id,
        _user_counts.c.entity,
        _user_counts.c.votes
    )
    .union_all(
        select(
            _anon_counts.c.url_id,
            _anon_counts.c.entity,
            _anon_counts.c.votes
        )
    )
    .cte("counts_record_type_union")
)


RECORD_TYPE_COUNTS_CTE = ValidatedCountsCTEContainer(
        (
            select(
                _union_counts.c.url_id,
                _union_counts.c.entity,
                func.sum(_union_counts.c.votes).label("votes")
            )
            .join(
                UnvalidatedURL,
                _union_counts.c.url_id == UnvalidatedURL.url_id
            )
            .group_by(
                _union_counts.c.url_id,
                _union_counts.c.entity,
            )
            .cte("counts_record_type")
        )
)