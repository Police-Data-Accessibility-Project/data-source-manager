from datetime import datetime

import pytest

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.core.tasks.scheduled.impl.sync.data_sources.params import DataSourcesSyncParameters
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_validated.enums import ValidatedURLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInfo
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.check import check_sync_concluded
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.core import \
    set_up_mock_pdap_client_responses, set_up_urls

from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error


@pytest.mark.asyncio
async def test_db_only(
    operator: SyncDataSourcesTaskOperator,
    adb_client_test: AsyncDatabaseClient,
    current_db_time: datetime
):
    """
    Test that operator does nothing with entries only in the database, and nothing is returned by the endpoint.
    """

    # Add URLs to database
    url_ids: list[int] = await set_up_urls(
        adb_client=adb_client_test,
        record_type=RecordType.COMPLAINTS_AND_MISCONDUCT,
        validated_type=None,
    )

    # Set up pdap client to return nothing
    set_up_mock_pdap_client_responses(
        operator.pdap_client,
        responses=[
            DataSourcesSyncResponseInfo(data_sources=[])
        ]
    )

    # Run operator
    run_info: TaskOperatorRunInfo = await operator.run_task()

    # Confirm operator ran without error
    assert_task_ran_without_error(run_info)

    # Check sync concluded
    assert operator.pdap_client.sync_data_sources.call_count == 1
    assert operator.pdap_client.sync_data_sources.call_args[0][0] == DataSourcesSyncParameters(
        cutoff_date=None,
        page=1
    )

    # Confirm URLs are unchanged in database
    urls: list[URL] = await adb_client_test.get_all(URL)
    assert len(urls) == len(url_ids)
    assert {url.id for url in urls} == set(url_ids)
    assert all(url.status == URLStatus.OK for url in urls)
    assert all(url.record_type == RecordType.COMPLAINTS_AND_MISCONDUCT for url in urls)

    # Confirm presence of sync status row with cutoff date and last updated at after initial db time
    await check_sync_concluded(
        adb_client_test,
        check_updated_at=False,
        current_db_datetime=current_db_time
    )

    # Confirm no validated flags
    flags: list[FlagURLValidated] = await adb_client_test.get_all(FlagURLValidated)
    assert len(flags) == 0
