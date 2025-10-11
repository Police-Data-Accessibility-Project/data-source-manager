from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_batch.sqlalchemy import LinkAgencyBatch
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class AutoGooglerAddAgencyQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        batch_id: int,
        agency_id: int,
    ):
        super().__init__()
        self.batch_id = batch_id
        self.agency_id = agency_id

    async def run(self, session: AsyncSession) -> str:
        """Add link and return agency name."""

        link = LinkAgencyBatch(
            batch_id=self.batch_id,
            agency_id=self.agency_id
        )
        session.add(link)

        query = (
            select(
                Agency.name
            )
        )

        return await sh.scalar(session, query=query)