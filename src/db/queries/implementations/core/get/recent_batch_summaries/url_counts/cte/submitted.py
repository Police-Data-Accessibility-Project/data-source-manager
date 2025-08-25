

from sqlalchemy import select, func

from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.data_source.sqlalchemy import URLDataSource
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.cte_container import \
    URLCountsCTEContainer

SUBMITTED_CTE = URLCountsCTEContainer(
    select(
        Batch.id,
        func.count(URL.id).label("submitted_count")
    )
    .join(
        LinkBatchURL,
        LinkBatchURL.batch_id == Batch.id,
    )
    .join(
        URL,
        URL.id == LinkBatchURL.url_id,
    )
    .join(
        URLDataSource,
        URLDataSource.url_id == URL.id,
    )
    .group_by(
        Batch.id
    ).cte("submitted_count")
)