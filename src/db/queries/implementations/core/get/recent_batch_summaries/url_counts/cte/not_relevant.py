from sqlalchemy import select, func

from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.cte_container import \
    URLCountsCTEContainer

NOT_RELEVANT_CTE = URLCountsCTEContainer(
    select(
        Batch.id,
        func.count(URL.id).label("not_relevant_count")
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
        FlagURLValidated,
        FlagURLValidated.url_id == URL.id,
    )
    .where(
        FlagURLValidated.type == URLType.NOT_RELEVANT
    )
    .group_by(
        Batch.id
    ).cte("not_relevant_count")
)