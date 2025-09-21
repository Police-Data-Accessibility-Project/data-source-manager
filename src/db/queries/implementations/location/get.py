from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import Location
from src.db.helpers.session import session_helper as sh
from src.db.queries.base.builder import QueryBuilderBase


class GetLocationQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        us_state_id: int,
        county_id: int | None = None,
        locality_id: int | None = None,
    ):
        super().__init__()
        self.us_state_id = us_state_id
        self.county_id = county_id
        self.locality_id = locality_id

    async def run(self, session: AsyncSession) -> int | None:
        query = (
            select(
                Location.id
            )
            .where(
                Location.state_id == self.us_state_id,
            )
        )
        if self.county_id is not None:
            query = query.where(
                Location.county_id == self.county_id
            )
        else:
            query = query.where(
                Location.county_id.is_(None)
            )

        if self.locality_id is not None:
            query = query.where(
                Location.locality_id == self.locality_id
            )
        else:
            query = query.where(
                Location.locality_id.is_(None)
            )

        return await sh.one_or_none(session, query=query)
