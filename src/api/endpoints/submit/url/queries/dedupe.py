from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.helpers.session import session_helper as sh
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class DeduplicateURLQueryBuilder(QueryBuilderBase):

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    async def run(self, session: AsyncSession) -> bool:

        query = select(
            URL.url
        ).where(
            URL.url == self.url
        )

        return await sh.has_results(session, query=query)





