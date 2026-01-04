from sqlalchemy import select, func

from src.core.tasks.url.operators.validate.queries.ctes.counts.constants import ANONYMOUS_VOTE_RATIO
from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer
from src.db.models.impl.annotation.agency.anon.sqlalchemy import AnnotationAgencyAnon
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.views.unvalidated_url import UnvalidatedURL

_user_counts = (
    select(
        AnnotationAgencyUser.url_id,
        AnnotationAgencyUser.agency_id.label("entity"),
        func.count().label("votes")
    )
    .group_by(
        AnnotationAgencyUser.url_id,
        AnnotationAgencyUser.agency_id
    )
)

_anon_counts = (
    select(
        AnnotationAgencyAnon.url_id,
        AnnotationAgencyAnon.agency_id.label("entity"),
        (func.count() / ANONYMOUS_VOTE_RATIO).label("votes")
    )
    .group_by(
        AnnotationAgencyAnon.url_id,
        AnnotationAgencyAnon.agency_id
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
    .cte("counts_agency_union")
)

AGENCY_VALIDATION_COUNTS_CTE = ValidatedCountsCTEContainer(
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
        .cte("counts_agency")
    )
)