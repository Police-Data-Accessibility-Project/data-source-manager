from fastapi import APIRouter, Depends

from src.api.dependencies import get_async_core
from src.api.endpoints.suggest.url.models.request import URLSuggestionRequest
from src.api.endpoints.suggest.url.models.response.model import URLSuggestResponse
from src.api.endpoints.suggest.url.wrapper import suggest_url_wrapper
from src.core.core import AsyncCore

suggest_router = APIRouter(prefix="/suggest", tags=["suggest"])

@suggest_router.post("/url")
async def suggest_url(
    request: URLSuggestionRequest,
    async_core: AsyncCore = Depends(get_async_core),
) -> URLSuggestResponse:
    return await suggest_url_wrapper(
        request=request,
        adb_client=async_core.adb_client,
    )
