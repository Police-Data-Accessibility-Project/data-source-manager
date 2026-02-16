from sqlalchemy import select, func

from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from src.db.models.impl.annotation.name.anon.sqlalchemy import AnnotationNameAnonEndorsement
from src.db.models.impl.annotation.name.user.sqlalchemy import AnnotationNameUserEndorsement
from src.db.models.views.unvalidated_url import UnvalidatedURL

_user_counts = (
    select(
        AnnotationNameSuggestion.url_id,
        AnnotationNameSuggestion.suggestion.label("entity"),
        func.count().label("votes")
    )
    .join(
        AnnotationNameUserEndorsement,
        AnnotationNameUserEndorsement.suggestion_id == AnnotationNameSuggestion.id
    )
    .group_by(
        AnnotationNameSuggestion.url_id,
        AnnotationNameSuggestion.suggestion
    )
    .cte("user_counts")
)

_anon_counts = (
    select(
        AnnotationNameSuggestion.url_id,
        AnnotationNameSuggestion.suggestion.label("entity"),
        func.count().label("votes")
    )
    .join(
        AnnotationNameAnonEndorsement,
        AnnotationNameAnonEndorsement.suggestion_id == AnnotationNameSuggestion.id
    )
    .group_by(
        AnnotationNameSuggestion.url_id,
        AnnotationNameSuggestion.suggestion
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