from sqlalchemy import select

from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.helpers import \
    get_exists_subtask_query
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.container import \
    SubtaskCTEContainer
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType

cte = (
    select(
        URL.id,
        get_exists_subtask_query(
            AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH
        )
    )
    .join(
        URLCompressedHTML
    )
    .cte("nlp_location_eligible")
)

NLP_LOCATION_CONTAINER = SubtaskCTEContainer(
    cte,
)