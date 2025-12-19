from sqlalchemy import select, func

from src.core.tasks.url.operators.validate.queries.ctes.counts.constants import ANONYMOUS_VOTE_RATIO
from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer
from src.db.models.impl.annotation.url_type.anon.sqlalchemy import AnnotationAnonURLType
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationUserURLType
from src.db.models.views.unvalidated_url import UnvalidatedURL

_user_counts = (
    select(
        AnnotationUserURLType.url_id,
        AnnotationUserURLType.type.label("entity"),
        func.count().label("votes")
    )
    .group_by(
        AnnotationUserURLType.url_id,
        AnnotationUserURLType.type
    )
)

_anon_counts = (
    select(
        AnnotationAnonURLType.url_id,
        AnnotationAnonURLType.url_type.label("entity"),
        (func.count() / ANONYMOUS_VOTE_RATIO).label("votes")
    )
    .group_by(
        AnnotationAnonURLType.url_id,
        AnnotationAnonURLType.url_type
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
        .cte("counts_url_type_union")
)

URL_TYPES_VALIDATION_COUNTS_CTE = ValidatedCountsCTEContainer(
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
        .cte("counts_url_type")
    )
)