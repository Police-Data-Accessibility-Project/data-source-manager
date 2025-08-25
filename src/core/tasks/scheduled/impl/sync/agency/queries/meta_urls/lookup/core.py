from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.impl.muckrock.api_interface.lookup_response import AgencyLookupResponse
from src.db.queries.base.builder import QueryBuilderBase


class LookupURLsQueryBuilder(QueryBuilderBase):
    """Look up URLS in database, providing mappings for those that exists."""

    def __init__(self, urls: list[str]):
        super().__init__()
        self.urls = urls

    async def run(self, session: AsyncSession) -> list[AgencyLookupResponse]:
        raise NotImplementedError