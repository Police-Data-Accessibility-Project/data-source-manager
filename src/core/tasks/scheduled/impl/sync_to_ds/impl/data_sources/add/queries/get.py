from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.sync.data_sources.add.request import AddDataSourcesOuterRequest


class DSAppSyncDataSourcesAddGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> AddDataSourcesOuterRequest:
        raise NotImplementedError