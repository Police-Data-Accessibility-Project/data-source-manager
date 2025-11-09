from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.sync.agencies.update.request import UpdateAgenciesOuterRequest


class DSAppSyncAgenciesUpdateGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> UpdateAgenciesOuterRequest:
        raise NotImplementedError