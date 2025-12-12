from sqlalchemy import select, func

from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer
from src.db.models.impl.link.anonymous_sessions__name_suggestion import LinkAnonymousSessionNameSuggestion
from src.db.models.impl.link.user_name_suggestion.sqlalchemy import LinkUserNameSuggestion
from src.db.models.impl.url.suggestion.name.sqlalchemy import URLNameSuggestion
from src.db.models.views.unvalidated_url import UnvalidatedURL

_user_counts = (
    select(
        URLNameSuggestion.url_id,
        URLNameSuggestion.suggestion.label("entity"),
        func.count().label("votes")
    )
    .join(
        LinkUserNameSuggestion,
        LinkUserNameSuggestion.suggestion_id == URLNameSuggestion.id
    )
    .group_by(
        URLNameSuggestion.url_id,
        URLNameSuggestion.suggestion
    )
    .cte("user_counts")
)

_anon_counts = (
    select(
        URLNameSuggestion.url_id,
        URLNameSuggestion.suggestion.label("entity"),
        func.count().label("votes")
    )
    .join(
        LinkAnonymousSessionNameSuggestion,
        LinkAnonymousSessionNameSuggestion.suggestion_id == URLNameSuggestion.id
    )
    .group_by(
        URLNameSuggestion.url_id,
        URLNameSuggestion.suggestion
    )
    .cte("anon_counts")
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
    .cte("counts_name_union")
)


NAME_VALIDATION_COUNTS_CTE = ValidatedCountsCTEContainer(
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
    ).cte("counts_name")
)