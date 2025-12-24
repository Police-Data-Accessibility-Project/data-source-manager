from pydantic import BaseModel
from sqlalchemy import select, func, RowMapping, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.proposals.agencies.approve.response import ProposalAgencyApproveResponse
from src.db.models.impl.agency.enums import JurisdictionType, AgencyType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.models.impl.proposals.agency_.core import ProposalAgency
from src.db.models.impl.proposals.agency_.decision_info import ProposalAgencyDecisionInfo
from src.db.models.impl.proposals.agency_.link__location import ProposalLinkAgencyLocation
from src.db.models.impl.proposals.enums import ProposalStatus
from src.db.queries.base.builder import QueryBuilderBase

class _ProposalAgencyIntermediateModel(BaseModel):
    proposal_id: int
    name: str
    agency_type: AgencyType
    jurisdiction_type: JurisdictionType | None
    proposal_status: ProposalStatus
    location_ids: list[int]

class ProposalAgencyApproveQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        proposed_agency_id: int,
        deciding_user_id: int
    ):
        super().__init__()
        self.proposed_agency_id = proposed_agency_id
        self.deciding_user_id = deciding_user_id

    async def run(self, session: AsyncSession) -> ProposalAgencyApproveResponse:

        # Get proposed agency
        proposed_agency: _ProposalAgencyIntermediateModel | None = await self._get_proposed_agency(session=session)
        if proposed_agency is None:
            return ProposalAgencyApproveResponse(
                message="Proposed agency not found.",
                success=False
            )

        # Confirm proposed agency is pending. Otherwise, fail early
        if proposed_agency.proposal_status != ProposalStatus.PENDING:
            return ProposalAgencyApproveResponse(
                message="Proposed agency is not pending.",
                success=False
            )

        await self._add_decision_info(session=session)

        promoted_agency_id: int = await self._add_promoted_agency(
            session=session,
            proposed_agency=proposed_agency
        )

        await self._add_location_links(
            session=session,
            promoted_agency_id=promoted_agency_id,
            location_ids=proposed_agency.location_ids
        )

        await self._update_proposed_agency_status(session=session)

        return ProposalAgencyApproveResponse(
            message="Proposed agency approved.",
            success=True,
            agency_id=promoted_agency_id
        )

    async def _get_proposed_agency(self, session: AsyncSession) -> _ProposalAgencyIntermediateModel | None:
        query = (
            select(
                ProposalAgency.id,
                ProposalAgency.name,
                ProposalAgency.agency_type,
                ProposalAgency.jurisdiction_type,
                ProposalAgency.proposal_status,
                func.array_agg(ProposalLinkAgencyLocation.location_id).label("location_ids")
            )
            .outerjoin(
                ProposalLinkAgencyLocation,
                ProposalLinkAgencyLocation.proposal_agency_id == ProposalAgency.id
            )
            .where(
                ProposalAgency.id == self.proposed_agency_id
            )
            .group_by(
                ProposalAgency.id,
                ProposalAgency.name,
                ProposalAgency.agency_type,
                ProposalAgency.jurisdiction_type
            )
        )
        try:
            mapping: RowMapping | None = await self.sh.mapping(session, query)
        except NoResultFound:
            return None
        return _ProposalAgencyIntermediateModel(
            proposal_id=mapping[ProposalAgency.id],
            name=mapping[ProposalAgency.name],
            agency_type=mapping[ProposalAgency.agency_type],
            jurisdiction_type=mapping[ProposalAgency.jurisdiction_type],
            proposal_status=mapping[ProposalAgency.proposal_status],
            location_ids=mapping["location_ids"] if mapping["location_ids"] != [None] else []
        )

    async def _add_decision_info(self, session: AsyncSession) -> None:
        decision_info = ProposalAgencyDecisionInfo(
            deciding_user_id=self.deciding_user_id,
            proposal_agency_id=self.proposed_agency_id,
        )
        session.add(decision_info)

    @staticmethod
    async def _add_promoted_agency(
        session: AsyncSession,
        proposed_agency: _ProposalAgencyIntermediateModel
    ) -> int:
        agency = Agency(
            name=proposed_agency.name,
            agency_type=proposed_agency.agency_type,
            jurisdiction_type=proposed_agency.jurisdiction_type,
        )
        session.add(agency)
        await session.flush()
        return agency.id

    @staticmethod
    async def _add_location_links(
        session: AsyncSession,
        promoted_agency_id: int,
        location_ids: list[int]
    ):
        links: list[LinkAgencyLocation] = []
        for location_id in location_ids:
            link = LinkAgencyLocation(
                agency_id=promoted_agency_id,
                location_id=location_id
            )
            links.append(link)
        session.add_all(links)

    async def _update_proposed_agency_status(self, session: AsyncSession) -> None:
        query = update(ProposalAgency).where(
            ProposalAgency.id == self.proposed_agency_id
        ).values(
            proposal_status=ProposalStatus.APPROVED
        )
        await session.execute(query)
