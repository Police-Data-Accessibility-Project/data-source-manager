from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.agencies.root.post.request import AgencyPostRequest
from src.api.endpoints.agencies.root.post.response import AgencyPostResponse
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.queries.base.builder import QueryBuilderBase


class AddAgencyQueryBuilder(QueryBuilderBase):

    def __init__(
            self,
            request: AgencyPostRequest,
    ):
        super().__init__()
        self.request = request

    async def run(self, session: AsyncSession) -> AgencyPostResponse:
        agency = Agency(
            name=self.request.name,
            agency_type=self.request.type,
            jurisdiction_type=self.request.jurisdiction_type,
        )

        session.add(agency)
        await session.flush()
        await session.refresh(agency)
        agency_id: int = agency.agency_id

        try:

            for location_id in self.request.location_ids:
                lal = LinkAgencyLocation(
                    agency_id=agency_id,
                    location_id=location_id,
                )
                session.add(lal)

        except Exception as e:
            await session.rollback()
            raise e

        return AgencyPostResponse(agency_id=agency_id)