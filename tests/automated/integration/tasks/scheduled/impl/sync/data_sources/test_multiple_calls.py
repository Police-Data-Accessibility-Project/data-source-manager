from datetime import datetime, timedelta

import pytest
from sqlalchemy import select

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.core.tasks.scheduled.impl.sync.data_sources.params import DataSourcesSyncParameters
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.state.sync.data_sources import DataSourcesSyncState
from src.db.models.impl.url.core.sqlalchemy import URL
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInfo
from src.external.pdap.enums import ApprovalStatus, DataSourcesURLStatus
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.core import \
    set_up_mock_pdap_client_responses, set_up_sync_response_info
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error


@pytest.mark.asyncio
async def test_ds_sync_multiple_calls(
    operator: SyncDataSourcesTaskOperator,
    adb_client_test: AsyncDatabaseClient,
    current_db_time: datetime,
    agency_ids: list[int]
):
    """
    Test that operator properly handles multiple calls to sync endpoint.
    """

    # Set up endpoint to return URLs on page 1 and 2, and stop on page 3
    set_up_mock_pdap_client_responses(
        mock_pdap_client=operator.pdap_client,
        responses=[
            set_up_sync_response_info(
                ids=[0, 1],
                record_type=RecordType.ACCIDENT_REPORTS,
                agency_ids=agency_ids,
                approval_status=ApprovalStatus.APPROVED,
                ds_url_status=DataSourcesURLStatus.OK,
            ),
            set_up_sync_response_info(
                ids=[2, 3],
                record_type=RecordType.ACCIDENT_REPORTS,
                agency_ids=agency_ids,
                approval_status=ApprovalStatus.APPROVED,
                ds_url_status=DataSourcesURLStatus.OK,
            ),
            DataSourcesSyncResponseInfo(
                data_sources=[],
            )
        ]
    )

    # Run operator
    run_info: TaskOperatorRunInfo = await operator.run_task()

    # Confirm operator ran without error
    assert_task_ran_without_error(run_info)


    # Confirm URLs are added to database
    urls: list[URL] = await adb_client_test.get_all(URL)
    assert all(url.status == URLStatus.OK for url in urls)
    assert all(url.record_type == RecordType.ACCIDENT_REPORTS for url in urls)
    url_ids: list[int] = [url.id for url in urls]

    # Confirm 3 calls to pdap_client.sync_data_sources
    assert operator.pdap_client.sync_data_sources.call_count == 3

    # Confirm sync status updated
    sync_state_results = await adb_client_test.scalar(
        select(
            DataSourcesSyncState
        )
    )
    assert sync_state_results.current_page is None
    assert sync_state_results.last_full_sync_at > current_db_time - timedelta(minutes=5)
    assert sync_state_results.current_cutoff_date > (current_db_time - timedelta(days=2)).date()

    set_up_mock_pdap_client_responses(
        mock_pdap_client=operator.pdap_client,
        responses=[
            DataSourcesSyncResponseInfo(
                data_sources=[],
            )
        ]
    )

    # Run operator again
    run_info: TaskOperatorRunInfo = await operator.run_task()

    # Confirm operator ran without error
    assert_task_ran_without_error(run_info)

    # Confirm no new URLs added
    urls: list[URL] = await adb_client_test.get_all(URL)
    assert set([url.id for url in urls]) == set(url_ids)

    # Confirm call to pdap_client.sync_data_sources made with cutoff_date
    assert operator.pdap_client.sync_data_sources.called_once_with(
        DataSourcesSyncParameters(
            cutoff_date=sync_state_results.current_cutoff_date,
            page=1
        )
    )