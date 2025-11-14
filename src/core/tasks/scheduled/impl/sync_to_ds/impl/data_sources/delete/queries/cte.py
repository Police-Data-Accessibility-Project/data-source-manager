"""
Data sources to be deleted from the DS database must be flagged for deletion
"""
from sqlalchemy import select, Column, CTE

from src.db.models.impl.flag.ds_delete.data_source import FlagDSDeleteDataSource
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource


class DSAppLinkSyncDataSourceDeletePrerequisitesCTEContainer:

    def __init__(self):
        self._cte = (
            select(
                DSAppLinkDataSource.ds_data_source_id
            )
            .join(
                FlagDSDeleteDataSource,
                FlagDSDeleteDataSource.ds_data_source_id == FlagDSDeleteDataSource.ds_data_source_id
            ).cte("ds_app_link_sync_data_source_delete_prerequisites")
        )

    @property
    def ds_data_source_id(self) -> Column[int]:
        return self._cte.columns.ds_data_source_id

    @property
    def cte(self) -> CTE:
        return self._cte