from sqlalchemy import select, func

from src.api.endpoints.metrics.batches.breakdown.templates.cte_ import BatchesBreakdownURLCTE
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL

PENDING_CTE = BatchesBreakdownURLCTE(
    select(
        Batch.id,
        func.count(LinkBatchURL.url_id).label("count_pending")
    )
    .join(
        LinkBatchURL,
        LinkBatchURL.batch_id == Batch.id
    )
    .outerjoin(
        FlagURLValidated,
        FlagURLValidated.url_id == LinkBatchURL.url_id
    )
    .where(
        FlagURLValidated.url_id.is_(None)
    )
    .group_by(Batch.id)
    .cte("pending")
)