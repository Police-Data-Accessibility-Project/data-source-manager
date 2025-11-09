from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.sync.data_sources.update.request import UpdateDataSourcesOuterRequest


class DSAppSyncDataSourcesUpdateGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> UpdateDataSourcesOuterRequest:
        raise NotImplementedError