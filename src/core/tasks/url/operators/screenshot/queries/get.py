from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.screenshot.constants import TASK_URL_LIMIT
from src.core.tasks.url.operators.screenshot.queries.cte import URLScreenshotPrerequisitesCTEContainer
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class GetURLsForScreenshotTaskQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[SimpleURLMapping]:
        cte = URLScreenshotPrerequisitesCTEContainer()

        query = select(
            cte.url_id,
            cte.url,
        ).limit(TASK_URL_LIMIT)

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)

        return [SimpleURLMapping(**mapping) for mapping in mappings]
