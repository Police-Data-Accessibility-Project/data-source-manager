from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_async_core
from src.api.endpoints.data_source.get.response import DataSourceGetResponse
from src.api.shared.models.message_response import MessageResponse
from src.core.core import AsyncCore

data_source_router = APIRouter(
    prefix="/data-source",
    tags=["data-source"]
)


@data_source_router.get("")
async def get_data_sources(
    async_core: AsyncCore = Depends(get_async_core),
    page: int = Query(
        description="Page number",
        default=1
    ),
) -> list[DataSourceGetResponse]:
    return await async_core.adb_client.run_query_builder(
        GetDataSourceQueryBuilder(page=page)
    )

@data_source_router.put("/{data_source_id}")
async def update_data_source(
    data_source_id: int,
    async_core: AsyncCore = Depends(get_async_core),
    request: DataSourceUpdateRequest,
) -> MessageResponse:
    return await async_core.adb_client.run_query_builder(
        UpdateDataSourceQueryBuilder(data_source_id=data_source_id, data_source_update=data_source_update)
    )
