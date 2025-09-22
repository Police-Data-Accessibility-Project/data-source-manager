from sqlalchemy import select, func

from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.views.unvalidated_url import UnvalidatedURL

URL_TYPES_VALIDATION_COUNTS_CTE = ValidatedCountsCTEContainer(
    (
        select(
            UserRecordTypeSuggestion.url_id,
            UserRecordTypeSuggestion.record_type.label("entity"),
            func.count().label("votes")
        )
        .join(
            UnvalidatedURL,
            UserRecordTypeSuggestion.url_id == UnvalidatedURL.url_id
        )
        .group_by(
            UserRecordTypeSuggestion.url_id,
            UserRecordTypeSuggestion.record_type
        )
        .cte("counts")
    )
)