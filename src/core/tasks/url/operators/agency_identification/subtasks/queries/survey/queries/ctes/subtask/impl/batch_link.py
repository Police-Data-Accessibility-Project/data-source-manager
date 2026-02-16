from sqlalchemy import select

from src.core.tasks.url.operators._shared.container.subtask.eligible import URLsSubtaskEligibleCTEContainer
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.helpers import \
    get_exists_subtask_query
from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.link.agency_batch.sqlalchemy import LinkAgencyBatch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL

cte = (
    select(
        URL.id,
        get_exists_subtask_query(
            AutoAgencyIDSubtaskType.BATCH_LINK,
        )
    )
    .join(
        LinkBatchURL,
        LinkBatchURL.url_id == URL.id,
    )
    .join(
        LinkAgencyBatch,
        LinkAgencyBatch.batch_id == LinkBatchURL.batch_id,
    )
    .cte("batch_link_eligible")
)

BATCH_LINK_SUBTASK_CONTAINER = URLsSubtaskEligibleCTEContainer(
    cte,
)