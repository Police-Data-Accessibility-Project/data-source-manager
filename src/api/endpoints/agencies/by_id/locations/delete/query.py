from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.queries.base.builder import QueryBuilderBase


class DeleteAgencyLocationQueryBuilder(QueryBuilderBase):

    def __init__(
            self,
            agency_id: int,
            location_id: int,
    ):
        super().__init__()
        self.agency_id = agency_id
        self.location_id = location_id

    async def run(self, session: AsyncSession) -> None:
        statement = (
            delete(LinkAgencyLocation)
            .where(
                (LinkAgencyLocation.agency_id == self.agency_id)
                & (LinkAgencyLocation.location_id == self.location_id)
            )
        )

        await session.execute(statement)

