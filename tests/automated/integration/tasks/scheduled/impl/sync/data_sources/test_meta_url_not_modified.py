import pytest

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_validated.enums import URLValidatedType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.external.pdap.enums import ApprovalStatus, DataSourcesURLStatus
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.core import set_up_urls, \
    set_up_mock_pdap_client_responses, set_up_sync_response_info
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_meta_url_not_modified(
    operator: SyncDataSourcesTaskOperator,
    adb_client_test: AsyncDatabaseClient,
    agency_ids: list[int],
    db_data_creator: DBDataCreator,
):
    """
    In a Data Source Sync, a validated Meta URL linked to an agency should be untouched
    if the sync response includes that same agency with other Data Sources URL
    """
    original_url_ids: list[int] = await set_up_urls(
        adb_client=adb_client_test,
        record_type=RecordType.CONTACT_INFO_AND_AGENCY_META,
        validated_type=URLValidatedType.META_URL,
    )
    # Link URLs to existing agencies
    await db_data_creator.create_url_agency_links(
        url_ids=original_url_ids,
        agency_ids=agency_ids,
    )

    set_up_mock_pdap_client_responses(
        mock_pdap_client=operator.pdap_client,
        responses=[
            set_up_sync_response_info(
                ids=[2, 3],
                record_type=RecordType.COMPLAINTS_AND_MISCONDUCT,
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

    # Confirm presence of 4 URLs in database
    urls: list[URL] = await adb_client_test.get_all(URL)
    assert len(urls) == 4
    assert all([url.status == URLStatus.OK for url in urls])
    assert set([url.record_type for url in urls]) == {
        RecordType.CONTACT_INFO_AND_AGENCY_META,
        RecordType.COMPLAINTS_AND_MISCONDUCT
    }
    all_url_ids: list[int] = [url.id for url in urls]
    # Check that all original URLs are present
    assert set(all_url_ids) >= set(original_url_ids)

    links: list[LinkURLAgency] = await adb_client_test.get_all(LinkURLAgency)
    assert len(links) == 16
    assert set(link.url_id for link in links) == set(all_url_ids)
    assert set(link.agency_id for link in links) == set(agency_ids)

    # Confirm presence of validated flag
    flags: list[FlagURLValidated] = await adb_client_test.get_all(FlagURLValidated)
    assert len(flags) == 4
    assert set([flag.type for flag in flags]) == {
        URLValidatedType.META_URL,
        URLValidatedType.DATA_SOURCE,
    }
    assert set(flag.url_id for flag in flags) == set(all_url_ids)

