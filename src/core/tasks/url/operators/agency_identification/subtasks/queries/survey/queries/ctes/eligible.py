from sqlalchemy import select

from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.exists.impl.high_confidence_annotations import \
    HIGH_CONFIDENCE_ANNOTATIONS_EXISTS_CONTAINER
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.exists.impl.validated import \
    VALIDATED_EXISTS_CONTAINER
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.impl.ckan import \
    CKAN_SUBTASK_CONTAINER
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.impl.homepage import \
    HOMEPAGE_SUBTASK_CONTAINER
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.impl.muckrock import \
    MUCKROCK_SUBTASK_CONTAINER
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.impl.nlp_location import \
    NLP_LOCATION_CONTAINER
from src.db.models.impl.url.core.sqlalchemy import URL

ELIGIBLE_CTE = (
    select(
        URL.id,
        CKAN_SUBTASK_CONTAINER.eligible_query.label("ckan"),
        MUCKROCK_SUBTASK_CONTAINER.eligible_query.label("muckrock"),
        HOMEPAGE_SUBTASK_CONTAINER.eligible_query.label("homepage"),
        NLP_LOCATION_CONTAINER.eligible_query.label("nlp_location"),
    )
    .where(
        HIGH_CONFIDENCE_ANNOTATIONS_EXISTS_CONTAINER.not_exists_query,
        VALIDATED_EXISTS_CONTAINER.not_exists_query,
    )
    .cte("eligible")
)