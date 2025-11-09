from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.sync.agencies.add.core import AddMetaURLsOuterRequest


class DSAppSyncMetaURLsAddGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> AddMetaURLsOuterRequest:
        raise NotImplementedError