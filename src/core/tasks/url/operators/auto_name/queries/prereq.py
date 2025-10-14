from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.auto_name.queries.cte import AutoNamePrerequisiteCTEContainer
from src.db.helpers.session import session_helper as sh
from src.db.queries.base.builder import QueryBuilderBase


class AutoNamePrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        cte = AutoNamePrerequisiteCTEContainer()
        query = select(cte.url_id)
        return await sh.results_exist(session, query=query)


