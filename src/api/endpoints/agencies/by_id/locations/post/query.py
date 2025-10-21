from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.queries.base.builder import QueryBuilderBase


class AddAgencyLocationQueryBuilder(QueryBuilderBase):

    def __init__(
            self,
            agency_id: int,
            location_id: int
    ):
        super().__init__()
        self.agency_id = agency_id
        self.location_id = location_id

    async def run(self, session: AsyncSession) -> None:
        lal = LinkAgencyLocation(
            agency_id=self.agency_id,
            location_id=self.location_id,
        )
        session.add(lal)