from sqlalchemy import select, func

from src.db.models.impl.url.core.sqlalchemy import URL

ALL_SUBQUERY = (
    select(
        func.count(URL.id).label("count")
    )
)