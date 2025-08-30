from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh

class LookupURLQueryBuilder(QueryBuilderBase):

    def __init__(self, urls: list[str]):
        super().__init__()
        self.urls: list[str] = urls

    async def run(self, session: AsyncSession) -> list[URLMapping]:
        query = (
            select(
                URL.id.label("url_id"),
                URL.url,
            )
            .where(
                URL.url.in_(self.urls),
            )
        )
        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        urls: list[URLMapping] = [
            URLMapping(**mapping) for mapping in mappings
        ]
        return urls