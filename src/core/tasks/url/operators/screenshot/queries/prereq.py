from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.screenshot.queries.cte import URLScreenshotPrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class URLsForScreenshotTaskPrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> Any:
        cte = URLScreenshotPrerequisitesCTEContainer()

        query = select(
            cte.url_id,
            cte.url,
        ).limit(1)

        return await sh.results_exist(session=session, query=query)
