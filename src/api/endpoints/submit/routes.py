from fastapi import APIRouter, Depends

from src.api.dependencies import get_async_core
from src.api.endpoints.submit.data_source.query import SubmitDataSourceURLProposalQueryBuilder

from src.api.endpoints.submit.data_source.models.response.duplicate import \
    SubmitDataSourceURLDuplicateSubmissionResponse
from src.api.endpoints.submit.data_source.models.response.standard import SubmitDataSourceURLProposalResponse
from src.api.endpoints.submit.data_source.request import DataSourceSubmissionRequest
from src.api.endpoints.submit.url.models.request import URLSubmissionRequest
from src.api.endpoints.submit.url.models.response import URLSubmissionResponse
from src.api.endpoints.submit.url.queries.core import SubmitURLQueryBuilder
from src.core.core import AsyncCore
from src.security.dtos.access_info import AccessInfo
from src.security.manager import get_access_info

submit_router = APIRouter(prefix="/submit", tags=["submit"])

@submit_router.post(
    "/url"
)
async def submit_url(
    request: URLSubmissionRequest,
    access_info: AccessInfo = Depends(get_access_info),
    async_core: AsyncCore = Depends(get_async_core),
) -> URLSubmissionResponse:
    return await async_core.adb_client.run_query_builder(
        SubmitURLQueryBuilder(
            request=request,
            user_id=access_info.user_id
        )
    )

@submit_router.post(
    "/data-source",
    response_model=SubmitDataSourceURLProposalResponse,
    responses={
        409: {
            "model": SubmitDataSourceURLDuplicateSubmissionResponse
        }
    }
)
async def submit_data_source(
    request: DataSourceSubmissionRequest,
    async_core: AsyncCore = Depends(get_async_core),
):
    return await async_core.adb_client.run_query_builder(
        SubmitDataSourceURLProposalQueryBuilder(
            request=request,
        )
    )
