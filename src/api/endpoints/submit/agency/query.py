from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.submit.agency.enums import AgencyProposalRequestStatus
from src.api.endpoints.submit.agency.helpers import \
    exact_duplicates_for_proposal_agency_query, exact_duplicates_for_approved_agency_query
from src.api.endpoints.submit.agency.request import SubmitAgencyRequestModel
from src.api.endpoints.submit.agency.response import SubmitAgencyProposalResponse
from src.db.models.impl.proposals.agency_.core import ProposalAgency
from src.db.models.impl.proposals.agency_.link__location import ProposalLinkAgencyLocation
from src.db.models.impl.proposals.enums import ProposalStatus
from src.db.queries.base.builder import QueryBuilderBase


class SubmitAgencyProposalQueryBuilder(QueryBuilderBase):

    def __init__(self, request: SubmitAgencyRequestModel, user_id: int):
        super().__init__()
        self.request = request
        self.user_id = user_id

    async def run(self, session: AsyncSession) -> SubmitAgencyProposalResponse:

        # Check that an agency with the same name AND location IDs does not exist
            # as an approved agency
        if await self._approved_agency_exists(session):
            return SubmitAgencyProposalResponse(
                status=AgencyProposalRequestStatus.ACCEPTED_DUPLICATE,
                details="An agency with the same properties is already approved."
            )

        # Check that an agency with the same name AND location IDs does not exist
            # as a proposed agency
        if await self._proposed_agency_exists(session):
            return SubmitAgencyProposalResponse(
                status=AgencyProposalRequestStatus.PROPOSAL_DUPLICATE,
                details="An agency with the same properties is already in the proposal queue."
            )

        # Add proposed agency and get proposal ID
        proposal_id: int = await self._add_proposed_agency(session)

        # Add proposed agency locations
        await self._add_proposed_agency_locations(
            session=session,
            proposal_id=proposal_id,
            location_ids=self.request.location_ids
        )

        # Return response

        return SubmitAgencyProposalResponse(
            proposal_id=proposal_id,
            status=AgencyProposalRequestStatus.SUCCESS,
            details="Successfully added proposed agency."
        )

    async def _approved_agency_exists(self, session: AsyncSession) -> bool:
        query = exact_duplicates_for_approved_agency_query(self.request)
        return await self.sh.results_exist(session, query=query)

    async def _proposed_agency_exists(self, session: AsyncSession) -> bool:
        query = exact_duplicates_for_proposal_agency_query(self.request)
        return await self.sh.results_exist(session, query=query)

    async def _add_proposed_agency(self, session: AsyncSession) -> int:
        proposal = ProposalAgency(
            name=self.request.name,
            jurisdiction_type=self.request.jurisdiction_type,
            agency_type=self.request.agency_type,
            proposing_user_id=self.user_id,
            proposal_status=ProposalStatus.PENDING,
        )
        session.add(proposal)
        await session.flush()
        return proposal.id

    async def _add_proposed_agency_locations(
        self,
        session: AsyncSession,
        location_ids: list[int],
        proposal_id: int
    ) -> None:
        for location_id in location_ids:
            link = ProposalLinkAgencyLocation(
                proposal_agency_id=proposal_id,
                location_id=location_id
            )
            session.add(link)
