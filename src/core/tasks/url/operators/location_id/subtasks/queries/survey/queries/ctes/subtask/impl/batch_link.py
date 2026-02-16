from sqlalchemy import select

from src.core.tasks.url.operators._shared.container.subtask.eligible import URLsSubtaskEligibleCTEContainer
from src.core.tasks.url.operators.location_id.subtasks.queries.survey.queries.ctes.subtask.helpers import \
    get_exists_subtask_query
from src.db.models.impl.annotation.location.auto.subtask.enums import LocationIDSubtaskType
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.link.location_batch.sqlalchemy import LinkLocationBatch
from src.db.models.impl.url.core.sqlalchemy import URL

cte = (
    select(
        URL.id,
        get_exists_subtask_query(
            LocationIDSubtaskType.BATCH_LINK
        )
    )
    .join(
        LinkBatchURL,
        LinkBatchURL.url_id == URL.id,
    )
    .join(
        LinkLocationBatch,
        LinkLocationBatch.batch_id == LinkBatchURL.batch_id,
    )
    .cte("batch_link")
)

BATCH_LINK_CONTAINER = URLsSubtaskEligibleCTEContainer(
    cte,
)
