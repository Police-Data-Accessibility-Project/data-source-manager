from sqlalchemy import select, func

from src.db.helpers.query import exists_url
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.task_error.sqlalchemy import URLTaskError
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.cte_container import \
    URLCountsCTEContainer

ERROR_CTE = URLCountsCTEContainer(
    select(
        Batch.id,
        func.count(URL.id).label("error_count")
    )
    .join(
        LinkBatchURL,
        LinkBatchURL.batch_id == Batch.id,
    )
    .join(
        URL,
        URL.id == LinkBatchURL.url_id,
    )
    .where(
        exists_url(URLTaskError)
    )
    .group_by(
        Batch.id
    ).cte("error_count")
)