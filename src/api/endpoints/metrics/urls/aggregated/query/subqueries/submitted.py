from sqlalchemy import func, select

from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.data_source.sqlalchemy import URLDataSource

SUBMITTED_SUBQUERY = (
    select(
        func.count(URL.id).label("count")
    )
    .join(
        URLDataSource,
        URL.id == URLDataSource.url_id,
    )
)