from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.pydantic.info import URLInfo
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.util.models.url_and_scheme import URLAndScheme
from src.util.url import get_url_and_scheme


class InsertURLQueryBuilder(QueryBuilderBase):


    def __init__(self, url_info: URLInfo):
        super().__init__()
        self.url_info = url_info

    async def run(self, session: AsyncSession) -> int:
        """Insert a new URL into the database."""
        url_and_scheme: URLAndScheme = get_url_and_scheme(self.url_info.url)
        url_entry = URL(
            url=url_and_scheme.url,
            scheme=url_and_scheme.scheme,
            collector_metadata=self.url_info.collector_metadata,
            status=self.url_info.status.value,
            source=self.url_info.source
        )
        if self.url_info.created_at is not None:
            url_entry.created_at = self.url_info.created_at
        session.add(url_entry)
        await session.flush()
        link = LinkBatchURL(
            batch_id=self.url_info.batch_id,
            url_id=url_entry.id
        )
        session.add(link)
        return url_entry.id