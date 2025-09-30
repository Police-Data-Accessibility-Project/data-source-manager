from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.submit.urls.queries.deduplicate.response import DeduplicateURLResponse
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class DeduplicateURLsQueryBuilder(QueryBuilderBase):

    def __init__(self, urls: list[str]):
        super().__init__()
        self.urls = urls

    async def run(self, session: AsyncSession) -> DeduplicateURLResponse:

        query = select(
            URL.url
        ).where(
            URL.url.in_(self.urls)
        )

        results: list[str] = await sh.scalars(session, query=query)
        results_set: set[str] = set(results)

        new_urls: list[str] = list(set(self.urls) - results_set)
        duplicate_urls: list[str] = list(set(self.urls) & results_set)

        return DeduplicateURLResponse(
            new_urls=new_urls,
            duplicate_urls=duplicate_urls,
        )




