import pytest

from src.api.endpoints.contributions.user.queries.core import GetUserContributionsQueryBuilder
from tests.automated.integration.readonly.helper import ReadOnlyTestHelper


@pytest.mark.asyncio
async def test_user(
    readonly_helper: ReadOnlyTestHelper
):
    for user_id in [
        readonly_helper.user_1_id,
        readonly_helper.user_2_id,
    ]:
        await readonly_helper.adb_client.run_query_builder(
            GetUserContributionsQueryBuilder(user_id)
        )
