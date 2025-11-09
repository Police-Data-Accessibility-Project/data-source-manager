from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_async_core
from src.api.endpoints.agencies.root.get.response import AgencyGetOuterResponse
from src.api.endpoints.meta_url.by_id.agencies.delete.wrapper import delete_meta_url_agency_link
from src.api.endpoints.meta_url.by_id.agencies.get.wrapper import get_meta_url_agencies_wrapper
from src.api.endpoints.meta_url.by_id.agencies.shared.check import check_is_meta_url
from src.api.endpoints.meta_url.by_id.post.wrapper import add_meta_url_agency_link
from src.api.endpoints.meta_url.get.query import GetMetaURLQueryBuilder
from src.api.endpoints.meta_url.get.response import MetaURLGetOuterResponse
from src.api.endpoints.meta_url.by_id.put.query import UpdateMetaURLQueryBuilder
from src.api.endpoints.meta_url.by_id.put.request import UpdateMetaURLRequest
from src.api.shared.models.message_response import MessageResponse
from src.core.core import AsyncCore

meta_urls_router = APIRouter(
    prefix="/meta-urls",
    tags=["meta-url"]
)

@meta_urls_router.get("")
async def get_meta_urls(
    async_core: AsyncCore = Depends(get_async_core),
    page: int = Query(
        description="Page number",
        default=1
    ),
) -> MetaURLGetOuterResponse:
    return await async_core.adb_client.run_query_builder(
        GetMetaURLQueryBuilder(page=page)
    )


@meta_urls_router.put("/{url_id}")
async def update_meta_url(
    url_id: int,
    request: UpdateMetaURLRequest,
    async_core: AsyncCore = Depends(get_async_core),
) -> MessageResponse:
    await check_is_meta_url(url_id=url_id, adb_client=async_core.adb_client)
    await async_core.adb_client.run_query_builder(
        UpdateMetaURLQueryBuilder(
            url_id=url_id,
            request=request
        )
    )
    return MessageResponse(message="Meta URL updated.")


@meta_urls_router.get("/{url_id}/agencies")
async def get_meta_url_agencies(
    url_id: int,
    async_core: AsyncCore = Depends(get_async_core),
) -> AgencyGetOuterResponse:
    return await get_meta_url_agencies_wrapper(
        url_id=url_id,
        adb_client=async_core.adb_client
    )

@meta_urls_router.post("/{url_id}/agencies/{agency_id}")
async def add_agency_to_meta_url(
    url_id: int,
    agency_id: int,
    async_core: AsyncCore = Depends(get_async_core),
) -> MessageResponse:
    await add_meta_url_agency_link(
        url_id=url_id,
        agency_id=agency_id,
        adb_client=async_core.adb_client
    )
    return MessageResponse(message="Agency added to meta URL.")

@meta_urls_router.delete("/{url_id}/agencies/{agency_id}")
async def remove_agency_from_meta_url(
    url_id: int,
    agency_id: int,
    async_core: AsyncCore = Depends(get_async_core),
) -> MessageResponse:
    await delete_meta_url_agency_link(
        url_id=url_id,
        agency_id=agency_id,
        adb_client=async_core.adb_client
    )
    return MessageResponse(message="Agency removed from meta URL.")
