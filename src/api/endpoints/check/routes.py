from fastapi import APIRouter, Depends

from src.api.dependencies import get_async_core
from src.api.endpoints.check.unique_url.response import CheckUniqueURLResponse
from src.api.endpoints.check.unique_url.wrapper import check_unique_url_wrapper
from src.core.core import AsyncCore

check_router = APIRouter(
    prefix="/check",
    tags=["check"]
)

@check_router.get("/unique-url")
async def check_unique_url(
    url: str,
    async_core: AsyncCore = Depends(get_async_core),
) -> CheckUniqueURLResponse:
    return await check_unique_url_wrapper(
        adb_client=async_core.adb_client,
        url=url
    )
