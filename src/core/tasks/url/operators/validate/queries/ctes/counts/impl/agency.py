from sqlalchemy import select, func

from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.views.unvalidated_url import UnvalidatedURL

AGENCY_VALIDATION_COUNTS_CTE = ValidatedCountsCTEContainer(
    (
            select(
                UserUrlAgencySuggestion.url_id,
                UserUrlAgencySuggestion.agency_id.label("entity"),
                func.count().label("votes")
            )
            .join(
                UnvalidatedURL,
                UserUrlAgencySuggestion.url_id == UnvalidatedURL.url_id
            )
            .group_by(
                UserUrlAgencySuggestion.url_id,
                UserUrlAgencySuggestion.agency_id
            )
            .cte("counts")
        )
)