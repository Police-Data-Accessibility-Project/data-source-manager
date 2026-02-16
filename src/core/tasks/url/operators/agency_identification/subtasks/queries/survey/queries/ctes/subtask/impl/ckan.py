from sqlalchemy import select

from src.collectors.enums import CollectorType
from src.core.tasks.url.operators._shared.container.subtask.eligible import URLsSubtaskEligibleCTEContainer
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.helpers import \
    get_exists_subtask_query
from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL

cte = (
    select(
        URL.id,
        get_exists_subtask_query(
            AutoAgencyIDSubtaskType.CKAN,
        ),
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
        Batch.strategy == CollectorType.CKAN.value,

    )
    .cte("ckan_eligible")
)

CKAN_SUBTASK_CONTAINER = URLsSubtaskEligibleCTEContainer(
    cte,
)