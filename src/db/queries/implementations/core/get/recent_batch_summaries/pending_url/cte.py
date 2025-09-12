from sqlalchemy import select, func, case, and_

from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL

PENDING_URL_CTE = (
    select(
        Batch.id.label("batch_id"),
        case(
            (
                and_(
                    func.count(LinkBatchURL.url_id) > func.count(FlagURLValidated.url_id),
                )
                , True),
            else_=False
        ).label("has_pending_urls")
    )
    .outerjoin(
        LinkBatchURL,
        LinkBatchURL.batch_id == Batch.id,
    )
    .outerjoin(
        FlagURLValidated,
        FlagURLValidated.url_id == LinkBatchURL.url_id,
    )
    .group_by(
        Batch.id
    ).cte("has_pending_urls")
)