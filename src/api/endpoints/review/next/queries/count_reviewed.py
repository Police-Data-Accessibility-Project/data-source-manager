from sqlalchemy import select, func

from src.api.endpoints.review.next.templates.count_cte import CountCTE
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL

COUNT_REVIEWED_CTE = CountCTE(
    select(
        Batch.id.label("batch_id"),
        func.count(FlagURLValidated.url_id).label("count")
    )
    .select_from(Batch)
    .join(LinkBatchURL)
    .outerjoin(FlagURLValidated, FlagURLValidated.url_id == LinkBatchURL.url_id)
    .group_by(Batch.id)
    .cte("count_reviewed")
)