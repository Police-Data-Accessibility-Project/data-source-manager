from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.agencies.by_id.locations.get.response import AgencyGetLocationsResponse
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.models.views.location_expanded import LocationExpandedView
from src.db.queries.base.builder import QueryBuilderBase


class GetAgencyLocationsQueryBuilder(QueryBuilderBase):

    def __init__(
            self,
            agency_id: int,
    ):
        super().__init__()
        self.agency_id = agency_id

    async def run(self, session: AsyncSession) -> list[AgencyGetLocationsResponse]:
        query = (
            select(
                LinkAgencyLocation.location_id,
                LocationExpandedView.full_display_name
            )
            .where(
                LinkAgencyLocation.agency_id == self.agency_id
            )
            .join(
                LocationExpandedView,
                LocationExpandedView.id == LinkAgencyLocation.location_id
            )
        )

        result: Sequence[RowMapping] = await self.sh.mappings(session, query=query)
        return [AgencyGetLocationsResponse(**row) for row in result]