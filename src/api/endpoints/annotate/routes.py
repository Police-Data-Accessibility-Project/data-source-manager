from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_async_core
from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse
from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.core.core import AsyncCore
from src.security.dtos.access_info import AccessInfo
from src.security.manager import get_access_info

annotate_router = APIRouter(
    prefix="/annotate",
    tags=["annotate"],
    responses={404: {"description": "Not found"}},
)

batch_query = Query(
    description="The batch id of the next URL to get. "
                "If not specified, defaults to first qualifying URL",
    default=None
)



@annotate_router.get("/all")
async def get_next_url_for_all_annotations(
        access_info: AccessInfo = Depends(get_access_info),
        async_core: AsyncCore = Depends(get_async_core),
        batch_id: int | None = batch_query
) -> GetNextURLForAllAnnotationResponse:
    return await async_core.get_next_url_for_all_annotations(
        batch_id=batch_id,
        user_id=access_info.user_id
    )

@annotate_router.post("/all/{url_id}")
async def annotate_url_for_all_annotations_and_get_next_url(
        url_id: int,
        all_annotation_post_info: AllAnnotationPostInfo,
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
        batch_id: int | None = batch_query
) -> GetNextURLForAllAnnotationResponse:
    """
    Post URL annotation and get next URL to annotate
    """
    await async_core.submit_url_for_all_annotations(
        user_id=access_info.user_id,
        url_id=url_id,
        post_info=all_annotation_post_info
    )
    return await async_core.get_next_url_for_all_annotations(
        batch_id=batch_id,
        user_id=access_info.user_id
    )