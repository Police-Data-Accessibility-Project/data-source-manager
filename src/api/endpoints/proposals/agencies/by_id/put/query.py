from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.proposals.agencies.by_id.put.request import ProposalAgencyPutRequest
from src.db.models.impl.proposals.agency_.core import ProposalAgency
from src.db.queries.base.builder import QueryBuilderBase


class UpdateProposalAgencyQueryBuilder(QueryBuilderBase):

    def __init__(
            self,
            agency_id: int,
            request: ProposalAgencyPutRequest,
    ):
        super().__init__()
        self.agency_id = agency_id
        self.request = request

    async def run(self, session: AsyncSession) -> None:

        query = (
            select(
                ProposalAgency
            )
            .where(
                ProposalAgency.id == self.agency_id
            )
        )

        agency: ProposalAgency | None = await self.sh.one_or_none(session, query=query)
        if not agency:
            raise HTTPException(status_code=400, detail="Proposed Agency not found")

        if self.request.name is not None:
            agency.name = self.request.name
        if self.request.type is not None:
            agency.agency_type = self.request.type
        if self.request.jurisdiction_type is not None:
            agency.jurisdiction_type = self.request.jurisdiction_type




