from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetDataSourceDuplicateQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url: str
    ):
        super().__init__()
        self.url = url

    async def run(self, session: AsyncSession) -> None:
        """
        Raises:
            HTTPException including details on the duplicate result.
        """

        query = (
            select(
                URL.status,
                FlagURLValidated.type
            )
            .outerjoin(
                FlagURLValidated,
                FlagURLValidated.url_id == URL.id
            )
            .where(
                URL.id == self.url_id
            )
        )
        mapping: RowMapping = await self.sh.mapping(
            query=query,
            session=session
        )

