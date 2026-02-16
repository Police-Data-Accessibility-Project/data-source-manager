from fastapi import APIRouter, Depends

from src.api.dependencies import get_async_core
from src.api.endpoints.locations.post.query import AddLocationQueryBuilder
from src.api.endpoints.locations.post.request import AddLocationRequestModel
from src.api.endpoints.locations.post.response import AddLocationResponseModel
from src.core.core import AsyncCore
from src.security.dtos.access_info import AccessInfo
from src.security.manager import get_admin_access_info

location_url_router = APIRouter(
    prefix="/locations",
    tags=["Locations"],
    responses={404: {"description": "Not found"}}
)

@location_url_router.post("")
async def create_location(
    request: AddLocationRequestModel,
    access_info: AccessInfo = Depends(get_admin_access_info),
    async_core: AsyncCore = Depends(get_async_core),
) -> AddLocationResponseModel:
    return await async_core.adb_client.run_query_builder(
        AddLocationQueryBuilder(request)
    )
