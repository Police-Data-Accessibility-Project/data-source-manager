from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.link.location_batch.sqlalchemy import LinkLocationBatch
from src.db.models.views.location_expanded import LocationExpandedView
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class AutoGooglerAddLocationQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        batch_id: int,
        location_id: int
    ):
        super().__init__()
        self.batch_id = batch_id
        self.location_id = location_id

    async def run(self, session: AsyncSession) -> str:
        """Add link and return location name."""

        link = LinkLocationBatch(
            batch_id=self.batch_id,
            location_id=self.location_id
        )
        session.add(link)

        query = (
            select(
                LocationExpandedView.full_display_name
            )
            .where(
                LocationExpandedView.id == self.location_id
            )
        )

        return await sh.scalar(session, query=query)
