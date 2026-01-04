from sqlalchemy import select, func

from src.api.endpoints.metrics.batches.breakdown.templates.cte_ import BatchesBreakdownURLCTE
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource

SUBMITTED_CTE = BatchesBreakdownURLCTE(
    select(
        Batch.id,
        func.count(DSAppLinkDataSource.id).label("count_submitted")
    )
    .join(
        LinkBatchURL,
        LinkBatchURL.batch_id == Batch.id
    )
    .join(
        DSAppLinkDataSource,
        DSAppLinkDataSource.url_id == LinkBatchURL.url_id
    )
    .group_by(Batch.id)
    .cte("submitted")
)