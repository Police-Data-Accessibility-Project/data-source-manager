from sqlalchemy import select, func

from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer
from src.db.models.impl.link.user_name_suggestion.sqlalchemy import LinkUserNameSuggestion
from src.db.models.impl.url.suggestion.name.sqlalchemy import URLNameSuggestion
from src.db.models.views.unvalidated_url import UnvalidatedURL

NAME_VALIDATION_COUNTS_CTE = ValidatedCountsCTEContainer(
    (
        select(
            URLNameSuggestion.url_id,
            URLNameSuggestion.suggestion.label("entity"),
            func.count().label("votes")
        )
        .join(
            UnvalidatedURL,
            URLNameSuggestion.url_id == UnvalidatedURL.url_id
        )
        .join(
            LinkUserNameSuggestion,
            LinkUserNameSuggestion.suggestion_id == URLNameSuggestion.id
        )
        .group_by(
            URLNameSuggestion.url_id,
            URLNameSuggestion.suggestion
        )
    ).cte("counts_name")
)