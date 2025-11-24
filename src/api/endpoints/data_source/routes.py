from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_async_core
from src.api.endpoints.agencies.root.get.response import AgencyGetResponse, AgencyGetOuterResponse
from src.api.endpoints.data_source.by_id.agency.delete.wrapper import delete_data_source_agency_link
from src.api.endpoints.data_source.by_id.agency.get.wrapper import get_data_source_agencies_wrapper
from src.api.endpoints.data_source.by_id.agency.post.wrapper import add_data_source_agency_link
from src.api.endpoints.data_source.by_id.agency.shared.check import check_is_data_source_url
from src.api.endpoints.data_source.by_id.get.query import GetDataSourceByIDQueryBuilder
from src.api.endpoints.data_source.get.query import GetDataSourcesQueryBuilder
from src.api.endpoints.data_source.get.response import DataSourceGetOuterResponse, DataSourceGetResponse
from src.api.endpoints.data_source.by_id.put.query import UpdateDataSourceQueryBuilder
from src.api.endpoints.data_source.by_id.put.request import DataSourcePutRequest
from src.api.shared.models.message_response import MessageResponse
from src.core.core import AsyncCore

data_sources_router = APIRouter(
    prefix="/data-sources",
    tags=["Data Sources"]
)


@data_sources_router.get("")
async def get_data_sources(
    async_core: AsyncCore = Depends(get_async_core),
    page: int = Query(
        description="Page number",
        default=1
    ),
) -> DataSourceGetOuterResponse:
    return await async_core.adb_client.run_query_builder(
        GetDataSourcesQueryBuilder(page=page)
    )

@data_sources_router.get("/{url_id}")
async def get_data_source_by_id(
    url_id: int,
    async_core: AsyncCore = Depends(get_async_core),
) -> DataSourceGetResponse:
    return await async_core.adb_client.run_query_builder(
        GetDataSourceByIDQueryBuilder(url_id)
    )

@data_sources_router.put("/{url_id}")
async def update_data_source(
    url_id: int ,
    request: DataSourcePutRequest,
    async_core: AsyncCore = Depends(get_async_core),
) -> MessageResponse:
    await check_is_data_source_url(url_id=url_id, adb_client=async_core.adb_client)
    await async_core.adb_client.run_query_builder(
        UpdateDataSourceQueryBuilder(
            url_id=url_id,
            request=request
        )
    )
    return MessageResponse(message="Data source updated.")

@data_sources_router.get("/{url_id}/agencies")
async def get_data_source_agencies(
    url_id: int,
    async_core: AsyncCore = Depends(get_async_core),
) -> AgencyGetOuterResponse:
    return await get_data_source_agencies_wrapper(
        url_id=url_id,
        adb_client=async_core.adb_client
    )

@data_sources_router.post("/{url_id}/agencies/{agency_id}")
async def add_agency_to_data_source(
    url_id: int,
    agency_id: int,
    async_core: AsyncCore = Depends(get_async_core),
) -> MessageResponse:
    await add_data_source_agency_link(
        url_id=url_id,
        agency_id=agency_id,
        adb_client=async_core.adb_client
    )
    return MessageResponse(message="Agency added to data source.")

@data_sources_router.delete("/{url_id}/agencies/{agency_id}")
async def remove_agency_from_data_source(
    url_id: int,
    agency_id: int,
    async_core: AsyncCore = Depends(get_async_core),
) -> MessageResponse:
    await delete_data_source_agency_link(
        url_id=url_id,
        agency_id=agency_id,
        adb_client=async_core.adb_client
    )
    return MessageResponse(message="Agency removed from data source.")

