from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.lookup.url.response import MetaURLLookupResponse
from src.db.queries.base.builder import QueryBuilderBase


class LookupMetaURLsQueryBuilder(QueryBuilderBase):
    """Lookup whether URLs exist in DB and are validated as meta URLs"""

    def __init__(self, urls: list[str]):
        super().__init__()
        self.urls = urls

    async def run(self, session: AsyncSession) -> list[MetaURLLookupResponse]:
        raise NotImplementedError