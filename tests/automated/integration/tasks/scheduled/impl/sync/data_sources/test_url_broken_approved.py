from datetime import datetime

import pytest

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.core.tasks.scheduled.impl.sync.data_sources.params import DataSourcesSyncParameters
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.external.pdap.enums import ApprovalStatus, DataSourcesURLStatus
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.check import check_sync_concluded
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.core import \
    set_up_mock_pdap_client_responses, set_up_sync_response_info
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error


@pytest.mark.asyncio
async def test_url_broken_approved(
    operator: SyncDataSourcesTaskOperator,
    adb_client_test: AsyncDatabaseClient,
    agency_ids: list[int],
    current_db_time: datetime
):
    """
    Test that a data source with
    - a broken URL status
    - an approved status
    Is added to the data source with a 404 Not Found status.
    """

    # Set up pdap client to return url with broken url status but approved
    set_up_mock_pdap_client_responses(
        mock_pdap_client=operator.pdap_client,
        responses=[
            set_up_sync_response_info(
                ids=[0, 1],
                record_type=RecordType.COMPLAINTS_AND_MISCONDUCT,
                agency_ids=agency_ids,
                approval_status=ApprovalStatus.APPROVED,
                ds_url_status=DataSourcesURLStatus.BROKEN,
            ),
        ]
    )

    # Run operator
    run_info: TaskOperatorRunInfo = await operator.run_task()

    # Confirm operator ran without error
    assert_task_ran_without_error(run_info)

    # Check sync concluded
    operator.pdap_client.sync_data_sources.call_count == 2

    # Confirm presence of URL with status of `404 not found`
    urls: list[URL] = await adb_client_test.get_all(URL)
    assert len(urls) == 2
    assert all([url.status == URLStatus.NOT_FOUND for url in urls])
    assert all([url.record_type == RecordType.COMPLAINTS_AND_MISCONDUCT for url in urls])
    url_ids: list[int] = [url.id for url in urls]

    # Confirm presence of agencies
    links: list[LinkURLAgency] = await adb_client_test.get_all(LinkURLAgency)
    assert len(links) == 8
    assert set(link.url_id for link in links) == set(url_ids)
    assert set(link.agency_id for link in links) == set(agency_ids)

    # Confirm presence of validated flag
    flags: list[FlagURLValidated] = await adb_client_test.get_all(FlagURLValidated)
    assert len(flags) == 2
    assert all([flag.type == URLType.DATA_SOURCE for flag in flags])
    assert set(flag.url_id for flag in flags) == set(url_ids)

    # Confirm presence of sync status row
    await check_sync_concluded(
        adb_client_test,
        current_db_datetime=current_db_time
    )



