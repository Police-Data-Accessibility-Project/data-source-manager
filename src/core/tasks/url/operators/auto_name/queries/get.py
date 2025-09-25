from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.auto_name.input import AutoNamePrerequisitesInput
from src.core.tasks.url.operators.auto_name.queries.cte import AutoNamePrerequisiteCTEContainer
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class AutoNameGetInputsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[AutoNamePrerequisitesInput]:
        cte = AutoNamePrerequisiteCTEContainer()
        query = select(cte.url_id, cte.content)

        mappings: Sequence[RowMapping] = await sh.mappings(session=session, query=query)
        results: list[AutoNamePrerequisitesInput] = []
        for mapping in mappings:
            result = AutoNamePrerequisitesInput(
                url_id=mapping["url_id"],
                title=mapping["content"],
            )
            results.append(result)

        return results