from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncMetaURLsDeleteGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[int]:
        """Get DS App links to delete."""
        raise NotImplementedError