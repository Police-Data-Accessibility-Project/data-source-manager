from datetime import datetime

import pytest
from sqlalchemy import select

from src.core.enums import RecordType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.state.sync.data_sources import DataSourcesSyncState
from src.db.models.impl.url.core.sqlalchemy import URL
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInfo
from src.external.pdap.enums import ApprovalStatus, DataSourcesURLStatus
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.core import patch_sync_data_sources, \
    set_up_mock_pdap_client_responses, set_up_sync_response_info
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error

@pytest.mark.asyncio
async def test_data_sources_sync_interruption(
    operator: SyncDataSourcesTaskOperator,
    adb_client_test: AsyncDatabaseClient,
    current_db_time: datetime,
    agency_ids: list[int]
):
    """
    Test that in the case of an interruption.
    The data sources sync will resume from the last processed page.
    """

    # Set up endpoint to return URLs on page 1, raise error on page 2
    # return URLs on page 2 on the second call, and return nothing on page 3
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
            ValueError("test ds sync error"),
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

    # Confirm presence of error
    assert run_info.outcome == TaskOperatorOutcome.ERROR
    assert "test ds sync error" in run_info.message

    # Confirm first URLs added to database
    urls: list[URL] = await adb_client_test.get_all(URL)
    assert len(urls) == 2

    # Confirm sync status updated to page 2 and cutoff date is null
    sync_state_results = await adb_client_test.scalar(
        select(
            DataSourcesSyncState
        )
    )
    assert sync_state_results.current_page == 2
    assert sync_state_results.last_full_sync_at is None
    assert sync_state_results.current_cutoff_date is None

    # Run operator again
    run_info: TaskOperatorRunInfo = await operator.run_task()

    # Confirm operator ran without error
    assert_task_ran_without_error(run_info)

    # Confirm second URLs added to database
    urls: list[URL] = await adb_client_test.get_all(URL)
    assert len(urls) == 4

    # Confirm page updated to null and cutoff date updated
    sync_state_results = await adb_client_test.scalar(
        select(
            DataSourcesSyncState
        )
    )
    assert sync_state_results.current_page is None
    assert sync_state_results.last_full_sync_at is not None
    assert sync_state_results.current_cutoff_date is not None
