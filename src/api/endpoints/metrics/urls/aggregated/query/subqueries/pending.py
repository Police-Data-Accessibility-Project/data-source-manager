from sqlalchemy import select, func

from src.collectors.enums import URLStatus
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL

PENDING_SUBQUERY = (
    select(
        func.count(URL.id).label("count")
    )
    .outerjoin(
        FlagURLValidated,
        URL.id == FlagURLValidated.url_id,
    )
    .where(
        URL.status == URLStatus.OK,
        FlagURLValidated.url_id.is_(None),
    )
)