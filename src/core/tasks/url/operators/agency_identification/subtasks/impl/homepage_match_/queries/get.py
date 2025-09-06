from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.queries.ctes.consolidated import \
    CONSOLIDATED_CTE
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh


class GetHomepageMatchSubtaskURLsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[int]:
        query = (
            select(
                CONSOLIDATED_CTE.c.url_id,
            ).distinct()
        )

        result: list[int] = await sh.scalars(session, query=query)
        return result

