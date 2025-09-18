from sqlalchemy import select

from src.collectors.enums import CollectorType
from src.core.tasks.url.operators._shared.container.subtask.eligible import URLsSubtaskEligibleCTEContainer
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.helpers import \
    get_exists_subtask_query
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType

cte = (
    select(
        URL.id,
        get_exists_subtask_query(
            AutoAgencyIDSubtaskType.MUCKROCK,
        )
    )
    .join(
        LinkBatchURL,
        LinkBatchURL.url_id == URL.id,
    )
    .join(
        Batch,
        Batch.id == LinkBatchURL.batch_id,
    )
    .where(
        Batch.strategy.in_(
            (CollectorType.MUCKROCK_ALL_SEARCH.value,
            CollectorType.MUCKROCK_COUNTY_SEARCH.value,
            CollectorType.MUCKROCK_SIMPLE_SEARCH.value,)
        ),
    )
    .cte("muckrock_eligible")
)

MUCKROCK_SUBTASK_CONTAINER = URLsSubtaskEligibleCTEContainer(
    cte,
)