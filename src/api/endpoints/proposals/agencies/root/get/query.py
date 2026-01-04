from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.api.endpoints.agencies.by_id.locations.get.response import AgencyGetLocationsResponse
from src.api.endpoints.proposals.agencies.root.get.response import ProposalAgencyGetOuterResponse, ProposalAgencyGetResponse
from src.db.models.impl.proposals.agency_.core import ProposalAgency
from src.db.models.impl.proposals.enums import ProposalStatus
from src.db.queries.base.builder import QueryBuilderBase


class ProposalAgencyGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> ProposalAgencyGetOuterResponse:
        query = (
            select(
                ProposalAgency
            ).where(
                ProposalAgency.proposal_status == ProposalStatus.PENDING
            ).options(
                joinedload(ProposalAgency.locations)
            )
        )
        proposal_agencies: Sequence[ProposalAgency] = (
            await session.execute(query)
        ).unique().scalars().all()
        if len(proposal_agencies) == 0:
            return ProposalAgencyGetOuterResponse(
                results=[]
            )
        responses: list[ProposalAgencyGetResponse] = []
        for proposal_agency in proposal_agencies:
            locations: list[AgencyGetLocationsResponse] = []
            for location in proposal_agency.locations:
                location = AgencyGetLocationsResponse(
                    location_id=location.id,
                    full_display_name=location.full_display_name,
                )
                locations.append(location)

            response = ProposalAgencyGetResponse(
                id=proposal_agency.id,
                name=proposal_agency.name,
                proposing_user_id=proposal_agency.proposing_user_id,
                agency_type=proposal_agency.agency_type,
                jurisdiction_type=proposal_agency.jurisdiction_type,
                created_at=proposal_agency.created_at,
                locations=locations
            )
            responses.append(response)

        return ProposalAgencyGetOuterResponse(
            results=responses
        )
