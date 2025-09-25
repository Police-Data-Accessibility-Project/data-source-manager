
from fastapi import APIRouter, Query, Depends, HTTPException
from starlette import status

from src.api.dependencies import get_async_core
from src.api.endpoints.search.agency.models.response import AgencySearchResponse
from src.api.endpoints.search.agency.query import SearchAgencyQueryBuilder
from src.api.endpoints.search.dtos.response import SearchURLResponse
from src.core.core import AsyncCore
from src.security.manager import get_access_info
from src.security.dtos.access_info import AccessInfo

search_router = APIRouter(prefix="/search", tags=["search"])


@search_router.get("/url")
async def search_url(
    url: str = Query(description="The URL to search for"),
    access_info: AccessInfo = Depends(get_access_info),
    async_core: AsyncCore = Depends(get_async_core),
) -> SearchURLResponse:
    """
    Search for a URL in the database
    """
    return await async_core.search_for_url(url)


@search_router.get("/agency")
async def search_agency(
    location_id: int | None = Query(
        description="The location id to search for",
        default=None
    ),
    query: str | None = Query(
        description="The query to search for",
        default=None
    ),
    access_info: AccessInfo = Depends(get_access_info),
    async_core: AsyncCore = Depends(get_async_core),
) -> list[AgencySearchResponse]:
    if query is None and location_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of query or location_id must be provided"
        )

    return await async_core.adb_client.run_query_builder(
        SearchAgencyQueryBuilder(
            location_id=location_id,
            query=query
        )
    )