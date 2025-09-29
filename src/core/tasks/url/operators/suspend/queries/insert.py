from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.suspend.queries.get.response import GetURLsForSuspensionResponse
from src.db.models.impl.flag.url_suspended.sqlalchemy import FlagURLSuspended
from src.db.queries.base.builder import QueryBuilderBase


class InsertURLSuspensionsQueryBuilder(QueryBuilderBase):

    def __init__(self, responses: list[GetURLsForSuspensionResponse]):
        super().__init__()
        self.responses = responses

    async def run(self, session: AsyncSession) -> Any:
        models: list[FlagURLSuspended] = []
        for response in self.responses:
            models.append(
                FlagURLSuspended(
                    url_id=response.url_id,
                )
            )
        session.add_all(models)
