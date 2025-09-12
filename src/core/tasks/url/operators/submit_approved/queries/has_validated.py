from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.enums import URLStatus
from src.db.models.impl.flag.url_validated.enums import URLValidatedType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class HasValidatedURLsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        query = (
            select(URL)
            .join(
                FlagURLValidated,
                FlagURLValidated.url_id == URL.id
            )
            .where(
                FlagURLValidated.type == URLValidatedType.DATA_SOURCE
            )
        )
        urls = await session.execute(query)
        urls = urls.scalars().all()
        return len(urls) > 0