from sqlalchemy import select, exists

from src.core.tasks.url.operators._shared.container.subtask.eligible import URLsSubtaskEligibleCTEContainer
from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.queries.ctes.consolidated import \
    CONSOLIDATED_CTE
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.helpers import \
    get_exists_subtask_query
from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.url.core.sqlalchemy import URL

VALID_URL_FLAG = (
    exists()
    .where(
        URL.id == CONSOLIDATED_CTE.c.url_id,
    )
)

cte = (
    select(
        URL.id,
        get_exists_subtask_query(
            AutoAgencyIDSubtaskType.HOMEPAGE_MATCH,
        )
    )
    .where(
        VALID_URL_FLAG,
    )
    .cte("homepage_eligible")
)

HOMEPAGE_SUBTASK_CONTAINER = URLsSubtaskEligibleCTEContainer(
    cte,
)