from sqlalchemy import CTE, select, exists
from sqlalchemy.orm import aliased

from src.collectors.enums import URLStatus
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.data_source.sqlalchemy import URLDataSource

VALIDATED_URLS_WITHOUT_DS_SQ =(
    select(URL)
    .join(
        FlagURLValidated,
        FlagURLValidated.url_id == URL.id
    )
    .where(
        URL.status == URLStatus.OK,
        FlagURLValidated.type == URLType.DATA_SOURCE,
        ~exists().where(
            URLDataSource.url_id == URL.id
        )
    )
    .subquery()
)

VALIDATED_URLS_WITHOUT_DS_ALIAS = aliased(
    URL,
    VALIDATED_URLS_WITHOUT_DS_SQ
)