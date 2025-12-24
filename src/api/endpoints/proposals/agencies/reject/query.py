from pydantic import BaseModel
from sqlalchemy import select, RowMapping, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.proposals.agencies.reject.request import ProposalAgencyRejectRequestModel
from src.api.endpoints.proposals.agencies.reject.response import ProposalAgencyRejectResponse
from src.db.models.impl.proposals.agency_.core import ProposalAgency
from src.db.models.impl.proposals.agency_.decision_info import ProposalAgencyDecisionInfo
from src.db.models.impl.proposals.enums import ProposalStatus
from src.db.queries.base.builder import QueryBuilderBase

class _ProposalAgencyIntermediateModel(BaseModel):
    proposal_id: int
    proposal_status: ProposalStatus


class ProposalAgencyRejectQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        deciding_user_id: int,
        proposed_agency_id: int,
        request_model: ProposalAgencyRejectRequestModel
    ):
        super().__init__()
        self.deciding_user_id = deciding_user_id
        self.proposed_agency_id = proposed_agency_id
        self.rejection_reason = request_model.rejection_reason

    async def run(self, session: AsyncSession) -> ProposalAgencyRejectResponse:
        # Get proposed agency
        proposed_agency: _ProposalAgencyIntermediateModel | None = await self._get_proposed_agency(session=session)
        if proposed_agency is None:
            return ProposalAgencyRejectResponse(
                message="Proposed agency not found.",
                success=False
            )

        # Confirm proposed agency is pending. Otherwise, fail early
        if proposed_agency.proposal_status != ProposalStatus.PENDING:
            return ProposalAgencyRejectResponse(
                message="Proposed agency is not pending.",
                success=False
            )

        await self._add_decision_info(session=session)
        await self._update_proposed_agency_status(session=session)

        return ProposalAgencyRejectResponse(
            message="Proposed agency rejected.",
            success=True
        )

    async def _get_proposed_agency(self, session: AsyncSession) -> _ProposalAgencyIntermediateModel | None:
        query = (
            select(
                ProposalAgency.id.label("proposal_id"),
                ProposalAgency.proposal_status
            )
            .where(
                ProposalAgency.id == self.proposed_agency_id
            )
        )
        mapping: RowMapping | None = await self.sh.mapping(session, query)
        if mapping is None:
            return None
        return _ProposalAgencyIntermediateModel(**mapping)

    async def _add_decision_info(self, session: AsyncSession) -> None:
        decision_info = ProposalAgencyDecisionInfo(
            proposal_agency_id=self.proposed_agency_id,
            rejection_reason=self.rejection_reason,
            deciding_user_id=self.deciding_user_id
        )
        session.add(decision_info)

    async def _update_proposed_agency_status(self, session: AsyncSession) -> None:
        query = update(ProposalAgency).where(
            ProposalAgency.id == self.proposed_agency_id
        ).values(
            proposal_status=ProposalStatus.REJECTED
        )
        await session.execute(query)
