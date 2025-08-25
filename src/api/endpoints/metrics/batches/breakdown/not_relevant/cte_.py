from sqlalchemy import select, func

from src.api.endpoints.metrics.batches.breakdown.templates.cte_ import BatchesBreakdownURLCTE
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.flag.url_validated.enums import ValidatedURLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL

NOT_RELEVANT_CTE = BatchesBreakdownURLCTE(
    select(
        Batch.id,
        func.count(FlagURLValidated.url_id).label("count_rejected")
    )
    .join(
        LinkBatchURL,
        LinkBatchURL.batch_id == Batch.id
    )
    .join(
        FlagURLValidated,
        FlagURLValidated.url_id == LinkBatchURL.url_id
    )
    .where(
        FlagURLValidated.type == ValidatedURLType.NOT_RELEVANT
    )
    .group_by(Batch.id)
    .cte("not_relevant")
)