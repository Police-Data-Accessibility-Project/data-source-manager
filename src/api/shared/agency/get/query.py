from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.endpoints.agencies.by_id.locations.get.response import AgencyGetLocationsResponse
from src.api.endpoints.agencies.root.get.response import AgencyGetResponse, AgencyGetOuterResponse
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.queries.base.builder import QueryBuilderBase


class GetRelatedAgenciesQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int
    ):
        super().__init__()
        self.url_id = url_id

    async def run(self, session: AsyncSession) -> AgencyGetOuterResponse:
        query = (
            select(
                Agency,
            )
            .options(
                selectinload(Agency.locations)
            )
            .join(
                LinkURLAgency,
                LinkURLAgency.agency_id == Agency.agency_id
            )
            .where(
                LinkURLAgency.url_id == self.url_id
            )
        )

        results: Sequence[RowMapping] = await self.sh.mappings(
            session,
            query=query
        )
        responses: list[AgencyGetResponse] = []
        for result in results:
            agency: Agency = result[Agency]
            locations: list[AgencyGetLocationsResponse] = [
                AgencyGetLocationsResponse(
                    location_id=location.id,
                    full_display_name=location.full_display_name,
                )
                for location in agency.locations
            ]
            responses.append(AgencyGetResponse(
                id=agency.agency_id,
                name=agency.name,
                type=agency.agency_type,
                jurisdiction_type=agency.jurisdiction_type,
                locations=locations,
            ))

        return AgencyGetOuterResponse(results=responses)
