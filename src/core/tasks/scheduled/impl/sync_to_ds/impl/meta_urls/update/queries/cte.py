from sqlalchemy import select, Column, CTE

from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL

class DSAppLinkSyncMetaURLUpdatePrerequisitesCTEContainer:

    def __init__(self):
        self._cte = (
            select(
                DSAppLinkMetaURL.url_id,
                DSAppLinkMetaURL.ds_meta_url_id,
            )
            .join(
                URL,
                URL.id == DSAppLinkMetaURL.url_id,
            )
            .where(
                URL.updated_at > DSAppLinkMetaURL.last_synced_at,
            ).cte("ds_app_link_sync_meta_url_update_prerequisites")
        )

    @property
    def url_id(self) -> Column[int]:
        return self._cte.columns.url_id

    @property
    def ds_meta_url_id(self) -> Column[int]:
        return self._cte.columns.ds_meta_url_id

    @property
    def cte(self) -> CTE:
        return self._cte