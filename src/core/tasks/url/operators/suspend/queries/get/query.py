from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.suspend.queries.cte import GetURLsForSuspensionCTEContainer
from src.core.tasks.url.operators.suspend.queries.get.response import GetURLsForSuspensionResponse
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh

class GetURLsForSuspensionQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[GetURLsForSuspensionResponse]:
        cte = GetURLsForSuspensionCTEContainer()
        results = await sh.mappings(session=session, query=cte.query)
        return [
            GetURLsForSuspensionResponse(url_id=result["url_id"])
            for result in results
        ]
