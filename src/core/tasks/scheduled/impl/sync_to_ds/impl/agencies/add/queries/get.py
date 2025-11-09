from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.sync.agencies.add.request import AddAgenciesOuterRequest


class DSAppSyncAgenciesAddGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> AddAgenciesOuterRequest:
        raise NotImplementedError