from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.integrity.queries.cte import IntegrityTaskCTEContainer
from src.db.queries.base.builder import QueryBuilderBase


class GetIntegrityTaskPrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> Any:
        cte = IntegrityTaskCTEContainer()
        return await self.sh.scalar(
            session=session,
            query=cte.any_rows_exist_query
        )
