from fastapi import APIRouter
from fastapi.params import Query, Depends, Path

from src.api.dependencies import get_async_core
from src.api.endpoints.agencies.by_id.delete.query import DeleteAgencyQueryBuilder
from src.api.endpoints.agencies.by_id.locations.delete.query import DeleteAgencyLocationQueryBuilder
from src.api.endpoints.agencies.by_id.locations.get.query import GetAgencyLocationsQueryBuilder
from src.api.endpoints.agencies.by_id.locations.get.response import AgencyGetLocationsResponse
from src.api.endpoints.agencies.by_id.locations.post.query import AddAgencyLocationQueryBuilder
from src.api.endpoints.agencies.by_id.put.query import UpdateAgencyQueryBuilder
from src.api.endpoints.agencies.by_id.put.request import AgencyPutRequest
from src.api.endpoints.agencies.root.get.query import GetAgenciesQueryBuilder
from src.api.endpoints.agencies.root.get.response import AgencyGetResponse
from src.api.endpoints.agencies.root.post.query import AddAgencyQueryBuilder
from src.api.endpoints.agencies.root.post.request import AgencyPostRequest
from src.api.endpoints.agencies.root.post.response import AgencyPostResponse
from src.api.shared.models.message_response import MessageResponse
from src.core.core import AsyncCore

agencies_router = APIRouter(prefix="/agencies", tags=["Agencies"])

@agencies_router.get("")
async def get_agencies(
    async_core: AsyncCore = Depends(get_async_core),
    page: int = Query(
        description="Page number",
        default=1
    ),
) -> list[AgencyGetResponse]:
    return await async_core.adb_client.run_query_builder(
        GetAgenciesQueryBuilder(page=page)
    )

@agencies_router.post("")
async def create_agency(
    request: AgencyPostRequest,
    async_core: AsyncCore = Depends(get_async_core),
) -> AgencyPostResponse:
    return await async_core.adb_client.run_query_builder(
        AddAgencyQueryBuilder(request=request)
    )

@agencies_router.delete("/{agency_id}")
async def delete_agency(
    agency_id: int = Path(
        description="Agency ID to delete"
    ),
    async_core: AsyncCore = Depends(get_async_core),
) -> MessageResponse:
    await async_core.adb_client.run_query_builder(
        DeleteAgencyQueryBuilder(agency_id=agency_id)
    )
    return MessageResponse(message="Agency deleted.")

@agencies_router.put("/{agency_id}")
async def update_agency(
    request: AgencyPutRequest,
    agency_id: int = Path(
        description="Agency ID to update"
    ),
    async_core: AsyncCore = Depends(get_async_core),
) -> MessageResponse:
    await async_core.adb_client.run_query_builder(
        UpdateAgencyQueryBuilder(agency_id=agency_id, request=request)
    )
    return MessageResponse(message="Agency updated.")

@agencies_router.get("/{agency_id}/locations")
async def get_agency_locations(
    agency_id: int = Path(
        description="Agency ID to get locations for"
    ),
    async_core: AsyncCore = Depends(get_async_core),
) -> list[AgencyGetLocationsResponse]:
    return await async_core.adb_client.run_query_builder(
        GetAgencyLocationsQueryBuilder(agency_id=agency_id)
    )

@agencies_router.post("/{agency_id}/locations/{location_id}")
async def add_location_to_agency(
    agency_id: int = Path(
        description="Agency ID to add location to"
    ),
    location_id: int = Path(
        description="Location ID to add"
    ),
    async_core: AsyncCore = Depends(get_async_core),
) -> MessageResponse:
    await async_core.adb_client.run_query_builder(
        AddAgencyLocationQueryBuilder(agency_id=agency_id, location_id=location_id)
    )
    return MessageResponse(message="Location added to agency.")

@agencies_router.delete("/{agency_id}/locations/{location_id}")
async def remove_location_from_agency(
    agency_id: int = Path(
        description="Agency ID to remove location from"
    ),
    location_id: int = Path(
        description="Location ID to remove"
    ),
    async_core: AsyncCore = Depends(get_async_core),
) -> MessageResponse:
    await async_core.adb_client.run_query_builder(
        DeleteAgencyLocationQueryBuilder(agency_id=agency_id, location_id=location_id)
    )
    return MessageResponse(message="Location removed from agency.")
