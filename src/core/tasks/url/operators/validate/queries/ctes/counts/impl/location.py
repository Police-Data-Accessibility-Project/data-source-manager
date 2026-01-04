from sqlalchemy import select, func

from src.core.tasks.url.operators.validate.queries.ctes.counts.constants import ANONYMOUS_VOTE_RATIO
from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer
from src.db.models.impl.annotation.location.anon.sqlalchemy import AnnotationLocationAnon
from src.db.models.impl.annotation.location.user.sqlalchemy import AnnotationLocationUser
from src.db.models.views.unvalidated_url import UnvalidatedURL

_user_counts = (
    select(
        AnnotationLocationUser.url_id,
        AnnotationLocationUser.location_id.label("entity"),
        func.count().label("votes")
    )
    .group_by(
        AnnotationLocationUser.url_id,
        AnnotationLocationUser.location_id
    )
)

_anon_counts = (
    select(
        AnnotationLocationAnon.url_id,
        AnnotationLocationAnon.location_id.label("entity"),
        (func.count() / ANONYMOUS_VOTE_RATIO).label("votes")
    )
    .group_by(
        AnnotationLocationAnon.url_id,
        AnnotationLocationAnon.location_id
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