from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.record_type.queries.cte import RecordTypeTaskPrerequisiteCTEContainer
from src.db.queries.base.builder import QueryBuilderBase


class RecordTypeTaskPrerequisiteQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        container = RecordTypeTaskPrerequisiteCTEContainer()
        query = (
            select(
                container.url_id
            )
        )
        return await self.sh.results_exist(session=session, query=query)

