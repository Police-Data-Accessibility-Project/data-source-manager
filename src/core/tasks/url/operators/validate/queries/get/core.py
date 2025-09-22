from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetURLsForAutoValidationQueryBuilder(QueryBuilderBase):


    async def run(self, session: AsyncSession) -> Any:
        # TODO (SM422): Implement

        query = (
            select(
                URL.id
            )
        )