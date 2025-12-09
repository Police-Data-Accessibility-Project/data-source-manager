from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.api.endpoints.agencies.by_id.locations.get.response import AgencyGetLocationsResponse
from src.api.endpoints.agencies.root.get.response import AgencyGetResponse
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.queries.base.builder import QueryBuilderBase


class GetAgenciesQueryBuilder(QueryBuilderBase):

    def __init__(
            self,
            page: int,
    ):
        super().__init__()
        self.page = page

    async def run(self, session: AsyncSession) -> list[AgencyGetResponse]:

        query = (
            select(
                Agency
            )
            .options(
                selectinload(Agency.locations)
            )
            .offset((self.page - 1) * 100)
            .limit(100)
        )

        results: Result[tuple[Agency]] = await session.execute(query)
        responses: list[AgencyGetResponse] = []
        for result in results:
            agency: Agency = result[0]
            locations: list[AgencyGetLocationsResponse] = [
                AgencyGetLocationsResponse(
                    location_id=location.id,
                    full_display_name=location.full_display_name,
                )
                for location in agency.locations
            ]
            responses.append(AgencyGetResponse(
                id=agency.id,
                name=agency.name,
                type=agency.agency_type,
                jurisdiction_type=agency.jurisdiction_type,
                locations=locations,
            ))

        return responses
