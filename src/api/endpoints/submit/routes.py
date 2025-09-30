from fastapi import APIRouter, Depends

from src.api.dependencies import get_async_core
from src.api.endpoints.submit.urls.models.request import URLSubmissionRequest
from src.api.endpoints.submit.urls.models.response import URLBatchSubmissionResponse
from src.core.core import AsyncCore
from src.security.dtos.access_info import AccessInfo
from src.security.manager import get_access_info

submit_router = APIRouter(prefix="/submit", tags=["submit"])

@submit_router.post("/urls")
async def submit_urls(
    urls: URLSubmissionRequest,
    access_info: AccessInfo = Depends(get_access_info),
    async_core: AsyncCore = Depends(get_async_core),
) -> URLBatchSubmissionResponse:
    raise NotImplementedError