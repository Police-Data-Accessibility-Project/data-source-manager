"""
Meta URLs to be deleted from the DS database must be flagged for deletion
"""
from sqlalchemy import Column, CTE, select

from src.db.models.impl.flag.ds_delete.meta_url import FlagDSDeleteMetaURL
from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL


class DSAppLinkSyncMetaURLDeletePrerequisitesCTEContainer:

    def __init__(self):
        self._cte = (
            select(
                DSAppLinkMetaURL.ds_meta_url_id
            )
            .join(
                FlagDSDeleteMetaURL,
                FlagDSDeleteMetaURL.ds_meta_url_id == DSAppLinkMetaURL.ds_meta_url_id
            ).cte()
        )

    @property
    def ds_meta_url_id(self) -> Column[int]:
        return self._cte.columns.ds_meta_url_id

    @property
    def cte(self) -> CTE:
        return self._cte