from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.flag.ds_delete.data_source import FlagDSDeleteDataSource
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncDataSourcesDeleteRemoveFlagsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        ds_data_source_ids: list[int]
    ):
        super().__init__()
        self._ds_data_source_ids = ds_data_source_ids

    async def run(self, session: AsyncSession) -> None:
        statement = (
            delete(FlagDSDeleteDataSource)
            .where(FlagDSDeleteDataSource.ds_data_source_id.in_(self._ds_data_source_ids))
        )
        await session.execute(statement)