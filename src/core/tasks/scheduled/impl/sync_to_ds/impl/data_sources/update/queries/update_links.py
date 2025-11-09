from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncDataSourcesUpdateAlterLinksQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        ds_data_source_ids: list[int]
    ):
        super().__init__()
        self._ds_data_source_ids = ds_data_source_ids

    async def run(self, session: AsyncSession) -> None:
        raise NotImplementedError