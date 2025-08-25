from sqlalchemy import select, func

from src.db.models.impl.flag.url_validated.enums import ValidatedURLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL

REJECTED_SUBQUERY = (
    select(
        func.count(URL.id).label("count")
    )
    .join(
        FlagURLValidated,
        URL.id == FlagURLValidated.url_id,
    )
    .where(
        FlagURLValidated.type == ValidatedURLType.NOT_RELEVANT,
    )
)