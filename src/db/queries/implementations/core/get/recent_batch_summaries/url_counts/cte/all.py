from sqlalchemy import select, func

from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.cte_container import \
    URLCountsCTEContainer

ALL_CTE = URLCountsCTEContainer(
    select(
        Batch.id,
        func.count(LinkBatchURL.url_id).label("total_count")
    )
    .join(
        LinkBatchURL,
        LinkBatchURL.batch_id == Batch.id,
    )
    .group_by(
        Batch.id
    ).cte("total_count")
)