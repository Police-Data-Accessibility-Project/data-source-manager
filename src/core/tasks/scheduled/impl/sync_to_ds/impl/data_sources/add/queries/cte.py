"""
Data sources to be added to the DS database must not have a
ds app link entry
"""
from sqlalchemy import select, exists, CTE, Column

from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource


class DSAppLinkSyncDataSourceAddPrerequisitesCTEContainer:

    def __init__(self):
        self._cte = (
            select(
                URL.id
            )
            .join(
                FlagURLValidated,
                FlagURLValidated.url_id == URL.id,
            )
            .where(
                FlagURLValidated.type == URLType.DATA_SOURCE,
                ~exists(
                    select(DSAppLinkDataSource.url_id)
                    .where(DSAppLinkDataSource.url_id == URL.id)
                )
            ).cte()
        )

    @property
    def url_id(self) -> Column[int]:
        return self._cte.columns.id

    @property
    def cte(self) -> CTE:
        return self._cte