import pytest

from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.update.queries.prereq import \
    DSAppSyncDataSourcesUpdatePrerequisitesQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient


@pytest.mark.asyncio
async def test_prereq(adb_client_test: AsyncDatabaseClient):
    await adb_client_test.run_query_builder(
        DSAppSyncDataSourcesUpdatePrerequisitesQueryBuilder()
    )

