from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.queries.base.builder import QueryBuilderBase


class DeleteAgencyQueryBuilder(QueryBuilderBase):

    def __init__(
            self,
            agency_id: int,
    ):
        super().__init__()
        self.agency_id = agency_id

    async def run(self, session: AsyncSession) -> None:
        statement = (
            delete(Agency)
            .where(Agency.agency_id == self.agency_id)
        )
        await session.execute(statement)