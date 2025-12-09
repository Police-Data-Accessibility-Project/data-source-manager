from sqlalchemy import update, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncDataSourcesUpdateAlterLinksQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        ds_data_source_ids: list[int]
    ):
        super().__init__()
        self._ds_data_source_ids = ds_data_source_ids

    async def run(self, session: AsyncSession) -> None:
        statement = (
            update(DSAppLinkDataSource)
            .where(DSAppLinkDataSource.ds_data_source_id.in_(self._ds_data_source_ids))
            .values({
                DSAppLinkDataSource.last_synced_at: func.now(),
            })
        )
        await session.execute(statement)