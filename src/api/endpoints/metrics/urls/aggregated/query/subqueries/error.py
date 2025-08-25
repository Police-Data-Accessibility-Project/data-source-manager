from sqlalchemy import select, func

from src.collectors.enums import URLStatus
from src.db.models.impl.url.core.sqlalchemy import URL

ERROR_SUBQUERY = (
    select(
        func.count(URL.id).label("count")
    )
    .where(URL.status == URLStatus.ERROR)
)