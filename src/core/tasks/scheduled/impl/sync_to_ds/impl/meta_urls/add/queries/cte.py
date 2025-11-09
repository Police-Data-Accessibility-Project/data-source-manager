"""
Meta URLs to be added to the DS database must not have a
ds app link entry
"""
from sqlalchemy import select, exists, Column, CTE

from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from src.db.models.views.meta_url import MetaURL


class DSAppLinkSyncMetaURLAddPrerequisitesCTEContainer:

    def __init__(self):
        self._cte = (
            select(
                MetaURL.url_id
            )
            .where(
                ~exists(
                    select(DSAppLinkMetaURL.url_id)
                    .where(DSAppLinkMetaURL.url_id == MetaURL.url_id)
                )
            ).cte()
        )

    @property
    def url_id(self) -> Column[int]:
        return self._cte.columns.url_id

    @property
    def cte(self) -> CTE:
        return self._cte