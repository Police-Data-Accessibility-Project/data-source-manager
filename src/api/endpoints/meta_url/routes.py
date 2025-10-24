from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_async_core
from src.api.shared.models.message_response import MessageResponse
from src.core.core import AsyncCore

meta_url_router = APIRouter(
    prefix="/meta-url",
    tags=["meta-url"]
)


@meta_url_router.get("")
async def get_meta_urls(
    async_core: AsyncCore = Depends(get_async_core),
    page: int = Query(
        description="Page number",
        default=1
    ),
) -> MetaURLGetResponse:
    return await async_core.adb_client.run_query_builder(GetMetaURLQueryBuilder())


@meta_url_router.put("/{meta_url_id}")
async def update_meta_url(
    meta_url_id: int,
    async_core: AsyncCore = Depends(get_async_core),
    request: MetaURLUpdateRequest,
) -> MessageResponse:
    return await async_core.adb_client.run_query_builder(
        UpdateMetaURLQueryBuilder(meta_url_id=meta_url_id, meta_url_update=meta_url_update)
    )


