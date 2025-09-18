from sqlalchemy import select

from src.core.tasks.url.operators._shared.subtask.container import SubtaskCTEContainer
from src.core.tasks.url.operators.location_id.subtasks.queries.survey.queries.ctes.subtask.helpers import \
    get_exists_subtask_query
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.suggestion.location.auto.subtask.enums import LocationIDSubtaskType

cte = (
    select(
        URL.id,
        get_exists_subtask_query(
            LocationIDSubtaskType.NLP_LOCATION_FREQUENCY
        )
    )
    .join(
        URLCompressedHTML,
    )
    .cte("nlp_location_eligible")
)

NLP_LOCATION_CONTAINER = SubtaskCTEContainer(
    cte,
)