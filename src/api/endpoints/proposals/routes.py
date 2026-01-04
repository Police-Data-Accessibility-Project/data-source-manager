from fastapi import APIRouter, Depends, Path

from src.api.dependencies import get_async_core
from src.api.endpoints.agencies.by_id.locations.get.response import AgencyGetLocationsResponse
from src.api.endpoints.proposals.agencies.by_id.approve.query import ProposalAgencyApproveQueryBuilder
from src.api.endpoints.proposals.agencies.by_id.approve.response import ProposalAgencyApproveResponse
from src.api.endpoints.proposals.agencies.by_id.locations.delete.query import DeleteProposalAgencyLocationQueryBuilder
from src.api.endpoints.proposals.agencies.by_id.locations.get.query import GetProposalAgencyLocationsQueryBuilder
from src.api.endpoints.proposals.agencies.by_id.locations.get.response import ProposalAgencyGetLocationsOuterResponse
from src.api.endpoints.proposals.agencies.by_id.locations.post.query import AddProposalAgencyLocationQueryBuilder
from src.api.endpoints.proposals.agencies.by_id.put.query import UpdateProposalAgencyQueryBuilder
from src.api.endpoints.proposals.agencies.by_id.put.request import ProposalAgencyPutRequest
from src.api.endpoints.proposals.agencies.root.get.query import ProposalAgencyGetQueryBuilder
from src.api.endpoints.proposals.agencies.root.get.response import ProposalAgencyGetOuterResponse
from src.api.endpoints.proposals.agencies.by_id.reject.query import ProposalAgencyRejectQueryBuilder
from src.api.endpoints.proposals.agencies.by_id.reject.request import ProposalAgencyRejectRequestModel
from src.api.endpoints.proposals.agencies.by_id.reject.response import ProposalAgencyRejectResponse
from src.api.shared.models.message_response import MessageResponse
from src.core.core import AsyncCore
from src.security.dtos.access_info import AccessInfo
from src.security.manager import get_admin_access_info

proposal_router = APIRouter(prefix="/proposal", tags=["Pending"])

@proposal_router.get("/agencies")
async def get_pending_agencies(
    async_core: AsyncCore = Depends(get_async_core),
    access_info: AccessInfo = Depends(get_admin_access_info),
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
    access_info: AccessInfo = Depends(get_admin_access_info),
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
    access_info: AccessInfo = Depends(get_admin_access_info),
) -> ProposalAgencyRejectResponse:
    return await async_core.adb_client.run_query_builder(
        ProposalAgencyRejectQueryBuilder(
            proposed_agency_id=proposed_agency_id,
            deciding_user_id=access_info.user_id,
            request_model=request,
        )
    )

@proposal_router.get("/agencies/{proposed_agency_id}/locations")
async def get_agency_locations(
    proposed_agency_id: int = Path(
        description="Agency ID to get locations for"
    ),
    async_core: AsyncCore = Depends(get_async_core),
) -> ProposalAgencyGetLocationsOuterResponse:
    return await async_core.adb_client.run_query_builder(
        GetProposalAgencyLocationsQueryBuilder(agency_id=proposed_agency_id)
    )

@proposal_router.post("/agencies/{proposed_agency_id}/locations/{location_id}")
async def add_location_to_agency(
    proposed_agency_id: int = Path(
        description="Agency ID to add location to"
    ),
    location_id: int = Path(
        description="Location ID to add"
    ),
    async_core: AsyncCore = Depends(get_async_core),
) -> MessageResponse:
    await async_core.adb_client.run_query_builder(
        AddProposalAgencyLocationQueryBuilder(agency_id=proposed_agency_id, location_id=location_id)
    )
    return MessageResponse(message="Location added to agency.")

@proposal_router.delete("/agencies/{proposed_agency_id}/locations/{location_id}")
async def remove_location_from_agency(
    proposed_agency_id: int = Path(
        description="Agency ID to remove location from"
    ),
    location_id: int = Path(
        description="Location ID to remove"
    ),
    async_core: AsyncCore = Depends(get_async_core),
) -> MessageResponse:
    await async_core.adb_client.run_query_builder(
        DeleteProposalAgencyLocationQueryBuilder(agency_id=proposed_agency_id, location_id=location_id)
    )
    return MessageResponse(message="Location removed from agency.")

@proposal_router.put("/agencies/{proposed_agency_id}")
async def update_agency(
    request: ProposalAgencyPutRequest,
    proposed_agency_id: int = Path(
        description="Agency ID to update"
    ),
    async_core: AsyncCore = Depends(get_async_core),
) -> MessageResponse:
    await async_core.adb_client.run_query_builder(
        UpdateProposalAgencyQueryBuilder(agency_id=proposed_agency_id, request=request)
    )
    return MessageResponse(message="Proposed agency updated.")
