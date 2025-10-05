from fastapi import APIRouter, Depends

from src.api.dependencies import get_async_core
from src.api.endpoints.contributions.leaderboard.query import GetContributionsLeaderboardQueryBuilder
from src.api.endpoints.contributions.leaderboard.response import ContributionsLeaderboardResponse
from src.api.endpoints.contributions.user.queries.core import GetUserContributionsQueryBuilder
from src.api.endpoints.contributions.user.response import ContributionsUserResponse
from src.core.core import AsyncCore
from src.security.dtos.access_info import AccessInfo
from src.security.manager import get_access_info

contributions_router = APIRouter(
    prefix="/contributions",
    tags=["Contributions"],
)

@contributions_router.get("/leaderboard")
async def get_leaderboard(
    core: AsyncCore = Depends(get_async_core),
    access_info: AccessInfo = Depends(get_access_info)
) -> ContributionsLeaderboardResponse:
    return await core.adb_client.run_query_builder(
        GetContributionsLeaderboardQueryBuilder()
    )

@contributions_router.get("/user")
async def get_user_contributions(
    core: AsyncCore = Depends(get_async_core),
    access_info: AccessInfo = Depends(get_access_info)
) -> ContributionsUserResponse:
    return await core.adb_client.run_query_builder(
        GetUserContributionsQueryBuilder(access_info.user_id)
    )