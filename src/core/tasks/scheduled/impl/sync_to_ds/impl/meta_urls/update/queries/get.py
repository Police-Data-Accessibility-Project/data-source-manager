from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.sync.meta_urls.update.request import UpdateMetaURLsOuterRequest


class DSAppSyncMetaURLsUpdateGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> UpdateMetaURLsOuterRequest:
        raise NotImplementedError