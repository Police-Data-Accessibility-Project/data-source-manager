from sqlalchemy import select, or_, Column, CTE

from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata


class DSAppLinkSyncDataSourceUpdatePrerequisitesCTEContainer:

    def __init__(self):
        self._cte = (
            select(
                DSAppLinkDataSource.url_id,
                DSAppLinkDataSource.ds_data_source_id,
            )
            .join(
                URL,
                URL.id == DSAppLinkDataSource.url_id,
            )
            .join(
                URLOptionalDataSourceMetadata,
                URL.id == URLOptionalDataSourceMetadata.url_id,
            )
            .where(
                or_(
                    URL.updated_at > DSAppLinkDataSource.last_synced_at,
                    URLOptionalDataSourceMetadata.updated_at > DSAppLinkDataSource.last_synced_at,
                )
            ).cte()
        )

    @property
    def url_id(self) -> Column[int]:
        return self._cte.columns.url_id

    @property
    def ds_data_source_id(self) -> Column[int]:
        return self._cte.columns.ds_data_source_id

    @property
    def cte(self) -> CTE:
        return self._cte