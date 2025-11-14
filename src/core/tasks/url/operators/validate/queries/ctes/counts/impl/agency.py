from sqlalchemy import select, func

from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer
from src.db.models.impl.url.suggestion.agency.user import UserURLAgencySuggestion
from src.db.models.views.unvalidated_url import UnvalidatedURL

AGENCY_VALIDATION_COUNTS_CTE = ValidatedCountsCTEContainer(
    (
            select(
                UserURLAgencySuggestion.url_id,
                UserURLAgencySuggestion.agency_id.label("entity"),
                func.count().label("votes")
            )
            .join(
                UnvalidatedURL,
                UserURLAgencySuggestion.url_id == UnvalidatedURL.url_id
            )
            .group_by(
                UserURLAgencySuggestion.url_id,
                UserURLAgencySuggestion.agency_id
            )
            .cte("counts_agency")
        )
)