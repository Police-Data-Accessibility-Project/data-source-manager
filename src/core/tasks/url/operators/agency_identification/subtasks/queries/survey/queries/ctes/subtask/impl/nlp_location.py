from operator import and_

from sqlalchemy import select

from src.core.tasks.url.operators._shared.container.subtask.eligible import URLsSubtaskEligibleCTEContainer
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.helpers import \
    get_exists_subtask_query
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.url.suggestion.location.auto.subtask.sqlalchemy import AutoLocationIDSubtask

cte = (
    select(
        URL.id,
        get_exists_subtask_query(
            AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH
        )
    )
    .join(
        AutoLocationIDSubtask,
        and_(
            AutoLocationIDSubtask.url_id == URL.id,
            AutoLocationIDSubtask.locations_found
        )
    )
    .cte("nlp_location_eligible")
)

NLP_LOCATION_CONTAINER = URLsSubtaskEligibleCTEContainer(
    cte,
)