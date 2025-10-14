from sqlalchemy import select, func

from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer
from src.db.models.impl.url.suggestion.location.user.sqlalchemy import UserLocationSuggestion
from src.db.models.views.unvalidated_url import UnvalidatedURL

LOCATION_VALIDATION_COUNTS_CTE = ValidatedCountsCTEContainer(
    (
            select(
                UserLocationSuggestion.url_id,
                UserLocationSuggestion.location_id.label("entity"),
                func.count().label("votes")
            )
            .join(
                UnvalidatedURL,
                UserLocationSuggestion.url_id == UnvalidatedURL.url_id
            )
            .group_by(
                UserLocationSuggestion.url_id,
                UserLocationSuggestion.location_id
            )
            .cte("counts_location")
        )
)