from fastapi import APIRouter, Depends, Path

from src.api.dependencies import get_async_core
from src.api.endpoints.proposals.agencies.approve.query import ProposalAgencyApproveQueryBuilder
from src.api.endpoints.proposals.agencies.approve.response import ProposalAgencyApproveResponse
from src.api.endpoints.proposals.agencies.get.query import ProposalAgencyGetQueryBuilder
from src.api.endpoints.proposals.agencies.get.response import ProposalAgencyGetOuterResponse
from src.api.endpoints.proposals.agencies.reject.query import ProposalAgencyRejectQueryBuilder
from src.api.endpoints.proposals.agencies.reject.request import ProposalAgencyRejectRequestModel
from src.api.endpoints.proposals.agencies.reject.response import ProposalAgencyRejectResponse
from src.core.core import AsyncCore
from src.security.dtos.access_info import AccessInfo
from src.security.manager import get_access_info

proposal_router = APIRouter(prefix="/proposal", tags=["Pending"])

@proposal_router.get("/agencies")
async def get_pending_agencies(
    async_core: AsyncCore = Depends(get_async_core),
    access_info: AccessInfo = Depends(get_access_info),
) -> ProposalAgencyGetOuterResponse:
    return await async_core.adb_client.run_query_builder(
        ProposalAgencyGetQueryBuilder(),
    )

@proposal_router.post("/agencies/{proposed_agency_id}/approve")
async def approve_proposed_agency(
    async_core: AsyncCore = Depends(get_async_core),
    proposed_agency_id: int = Path(
        description="Proposed agency ID to approve"
    ),
    access_info: AccessInfo = Depends(get_access_info),
) -> ProposalAgencyApproveResponse:
    return await async_core.adb_client.run_query_builder(
        ProposalAgencyApproveQueryBuilder(
            proposed_agency_id=proposed_agency_id,
            deciding_user_id=access_info.user_id,
        )
    )

@proposal_router.post("/agencies/{proposed_agency_id}/reject")
async def reject_proposed_agency(
    request: ProposalAgencyRejectRequestModel,
    async_core: AsyncCore = Depends(get_async_core),
    proposed_agency_id: int = Path(
        description="Proposed agency ID to reject"
    ),
    access_info: AccessInfo = Depends(get_access_info),
) -> ProposalAgencyRejectResponse:
    return await async_core.adb_client.run_query_builder(
        ProposalAgencyRejectQueryBuilder(
            proposed_agency_id=proposed_agency_id,
            deciding_user_id=access_info.user_id,
            request_model=request,
        )
    )