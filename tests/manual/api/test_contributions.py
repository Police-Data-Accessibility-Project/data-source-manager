import pytest

from src.api.endpoints.contributions.leaderboard.query import GetContributionsLeaderboardQueryBuilder
from src.api.endpoints.contributions.user.queries.core import GetUserContributionsQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient

# 72 = Max
# 17 = Josh

@pytest.mark.asyncio
async def test_contributions(
    adb_client_test: AsyncDatabaseClient
):

    response =await adb_client_test.run_query_builder(
        GetUserContributionsQueryBuilder(user_id=17)
    )
    print(response)
    #
    # await adb_client_test.run_query_builder(
    #     GetContributionsLeaderboardQueryBuilder()
    # )