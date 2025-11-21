from sqlalchemy import select, func

from src.api.endpoints.metrics.batches.breakdown.templates.cte_ import BatchesBreakdownURLCTE
from src.db.helpers.query import exists_url
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.task_error.sqlalchemy import URLTaskError

URL_ERROR_CTE = BatchesBreakdownURLCTE(
    select(
        Batch.id,
        func.count(LinkBatchURL.url_id).label("count_error")
    )
    .join(
        LinkBatchURL,
        LinkBatchURL.batch_id == Batch.id
    )
    .join(
        URL,
        URL.id == LinkBatchURL.url_id
   )
    .where(
        exists_url(URLTaskError)
    )
    .group_by(Batch.id)
    .cte("error")
)
