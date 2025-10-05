import pytest

from src.api.endpoints.contributions.user.queries import GetUserContributionsQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient


@pytest.mark.asyncio
async def test_contributions(
    adb_client_test: AsyncDatabaseClient
):

    await adb_client_test.run_query_builder(
        GetUserContributionsQueryBuilder(user_id=72)
    )