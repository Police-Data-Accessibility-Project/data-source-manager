from sqlalchemy import select, func

from src.api.endpoints.metrics.batches.breakdown.templates.cte_ import BatchesBreakdownURLCTE
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL

TOTAL_CTE = BatchesBreakdownURLCTE(
    select(
        Batch.id,
        func.count(LinkBatchURL.url_id).label("count_total")
    )
    .join(LinkBatchURL)
    .group_by(Batch.id)
    .cte("total")
)