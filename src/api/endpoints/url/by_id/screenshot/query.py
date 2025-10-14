from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.url.screenshot.sqlalchemy import URLScreenshot
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class GetURLScreenshotQueryBuilder(QueryBuilderBase):

    def __init__(self, url_id: int):
        super().__init__()
        self.url_id = url_id

    async def run(self, session: AsyncSession) -> bytes | None:

        query = (
            select(URLScreenshot.content)
            .where(URLScreenshot.url_id == self.url_id)
        )

        return await sh.one_or_none(
            session=session,
            query=query
        )

