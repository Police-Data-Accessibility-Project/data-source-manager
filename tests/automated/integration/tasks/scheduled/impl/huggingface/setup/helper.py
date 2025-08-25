from src.db.client.async_ import AsyncDatabaseClient
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.models.input import \
    TestPushToHuggingFaceURLSetupEntryInput
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.queries.setup import \
    SetupTestPushToHuggingFaceEntryQueryBuilder


async def setup_urls(
    dbc: AsyncDatabaseClient,
    inp: TestPushToHuggingFaceURLSetupEntryInput
) -> list[int]:
    # Set up 2 URLs
    builder = SetupTestPushToHuggingFaceEntryQueryBuilder(inp)
    return await dbc.run_query_builder(builder)


