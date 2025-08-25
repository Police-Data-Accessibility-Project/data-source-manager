from sqlalchemy import select, func, CTE, Column

from src.collectors.enums import URLStatus
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.api.endpoints.metrics.batches.breakdown.templates.cte_ import BatchesBreakdownURLCTE
from src.db.models.impl.url.core.sqlalchemy import URL

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
    .where(URL.status == URLStatus.ERROR)
    .group_by(Batch.id)
    .cte("error")
)
