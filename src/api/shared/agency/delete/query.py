from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.queries.base.builder import QueryBuilderBase


class RemoveURLAgencyLinkQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int,
        agency_id: int
    ):
        super().__init__()
        self.url_id = url_id
        self.agency_id = agency_id

    async def run(self, session: AsyncSession) -> None:
        statement = (
            delete(
                LinkURLAgency
            )
            .where(
                LinkURLAgency.url_id == self.url_id,
                LinkURLAgency.agency_id == self.agency_id
            )
        )
        await session.execute(statement)