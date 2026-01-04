import pytest

from src.api.endpoints.contributions.leaderboard.query import GetContributionsLeaderboardQueryBuilder
from tests.automated.integration.readonly.helper import ReadOnlyTestHelper


@pytest.mark.asyncio
async def test_leaderboard(
    readonly_helper: ReadOnlyTestHelper
):
    await readonly_helper.adb_client.run_query_builder(
        GetContributionsLeaderboardQueryBuilder()
    )

