from sqlalchemy import select, func

from src.core.tasks.url.operators.validate.queries.ctes.counts.constants import ANONYMOUS_VOTE_RATIO
from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer
from src.db.models.impl.url.suggestion.anonymous.location.sqlalchemy import AnonymousAnnotationLocation
from src.db.models.impl.url.suggestion.anonymous.url_type.sqlalchemy import AnonymousAnnotationURLType
from src.db.models.impl.url.suggestion.location.user.sqlalchemy import UserLocationSuggestion
from src.db.models.views.unvalidated_url import UnvalidatedURL

_user_counts = (
    select(
        UserLocationSuggestion.url_id,
        UserLocationSuggestion.location_id.label("entity"),
        func.count().label("votes")
    )
    .group_by(
        UserLocationSuggestion.url_id,
        UserLocationSuggestion.location_id
    )
)

_anon_counts = (
    select(
        AnonymousAnnotationLocation.url_id,
        AnonymousAnnotationLocation.location_id.label("entity"),
        (func.count() / ANONYMOUS_VOTE_RATIO).label("votes")
    )
    .group_by(
        AnonymousAnnotationLocation.url_id,
        AnonymousAnnotationLocation.location_id
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
    .cte("counts_location_union")
)

LOCATION_VALIDATION_COUNTS_CTE = ValidatedCountsCTEContainer(
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
        .cte("counts_location")
    )
)