from sqlalchemy import select, func

from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer
from src.db.models.impl.url.suggestion.url_type.user import UserURLTypeSuggestion
from src.db.models.views.unvalidated_url import UnvalidatedURL

URL_TYPES_VALIDATION_COUNTS_CTE = ValidatedCountsCTEContainer(
    (
        select(
            UserURLTypeSuggestion.url_id,
            UserURLTypeSuggestion.type.label("entity"),
            func.count().label("votes")
        )
        .join(
            UnvalidatedURL,
            UserURLTypeSuggestion.url_id == UnvalidatedURL.url_id
        )
        .group_by(
            UserURLTypeSuggestion.url_id,
            UserURLTypeSuggestion.type
        )
        .cte("counts_url_type")
    )
)