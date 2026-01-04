from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.integrity.queries.cte import IntegrityTaskCTEContainer
from src.db.queries.base.builder import QueryBuilderBase


class GetIntegrityTaskDataQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[str]:
        cte = IntegrityTaskCTEContainer()
        mapping: RowMapping = await self.sh.mapping(
            session=session,
            query=cte.select_all_columns_query
        )
        return [
            model.__tablename__
            for model in cte.models
            if mapping[model.__tablename__]
        ]