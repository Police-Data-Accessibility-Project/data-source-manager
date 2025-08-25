import pytest

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_validated.enums import ValidatedURLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.external.pdap.enums import ApprovalStatus, DataSourcesURLStatus
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.core import \
    set_up_mock_pdap_client_responses, set_up_sync_response_info
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error


@pytest.mark.asyncio
async def test_url_ok_approved(
    operator: SyncDataSourcesTaskOperator,
    adb_client_test: AsyncDatabaseClient,
    agency_ids: list[int]
):
    """
    Test that a URL with an OK URL status and an approved status
    is added to the database with an OK status
    and a validated flag with `submitted=True`
    """

    # Set up pdap client to return url with ok url status and approved
    set_up_mock_pdap_client_responses(
        mock_pdap_client=operator.pdap_client,
        responses=[
            set_up_sync_response_info(
                ids=[0, 1],
                record_type=RecordType.OTHER,
                agency_ids=agency_ids,
                approval_status=ApprovalStatus.APPROVED,
                ds_url_status=DataSourcesURLStatus.OK,
            ),
        ]
    )

    # Run operator
    run_info: TaskOperatorRunInfo = await operator.run_task()

    # Confirm operator ran without error
    assert_task_ran_without_error(run_info)

    # Check sync concluded
    operator.pdap_client.sync_data_sources.call_count == 2

    # Confirm URL is added to database with OK status
    urls: list[URL] = await adb_client_test.get_all(URL)
    assert len(urls) == 2
    assert all([url.status == URLStatus.OK for url in urls])
    assert all([url.record_type == RecordType.OTHER for url in urls])
    url_ids: list[int] = [url.id for url in urls]

    # Confirm presence of validated flag
    flags: list[FlagURLValidated] = await adb_client_test.get_all(FlagURLValidated)
    assert len(flags) == 2
    assert all([flag.type == ValidatedURLType.DATA_SOURCE for flag in flags])
    assert set(flag.url_id for flag in flags) == set(url_ids)
