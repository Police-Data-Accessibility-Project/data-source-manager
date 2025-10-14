
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.auto_relevant.queries.cte import AutoRelevantPrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh

class AutoRelevantPrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:

        cte = AutoRelevantPrerequisitesCTEContainer()
        query = (
            select(cte.url_alias)
        )

        return await sh.results_exist(session, query=query)