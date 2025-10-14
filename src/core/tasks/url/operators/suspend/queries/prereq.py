from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.suspend.queries.cte import GetURLsForSuspensionCTEContainer
from src.db.helpers.session import session_helper as sh
from src.db.queries.base.builder import QueryBuilderBase


class GetURLsForSuspensionPrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        cte = GetURLsForSuspensionCTEContainer()
        return await sh.results_exist(session=session, query=cte.query)
