import pytest

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.external.pdap.enums import ApprovalStatus, DataSourcesURLStatus
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.core import set_up_urls, \
    set_up_mock_pdap_client_responses, set_up_sync_response_info
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error


@pytest.mark.asyncio
async def test_url_in_db_overwritten_by_ds(
    operator: SyncDataSourcesTaskOperator,
    adb_client_test: AsyncDatabaseClient,
    agency_ids: list[int]
):
    """
    Test that a URL in the database is overwritten by a data source with the same URL,
    if their information is different. 
    """
    old_agency_ids: list[int] = agency_ids[:2]
    new_agency_ids: list[int] = agency_ids[2:4]


    # Add URLs to database
    url_ids: list[int] = await set_up_urls(
        adb_client=adb_client_test,
        record_type=RecordType.COMPLAINTS_AND_MISCONDUCT,
        validated_type=URLType.DATA_SOURCE,
    )
    # Link URLs to 2 existing agencies
    links: list[LinkURLAgency] = []
    for url_id in url_ids:
        for agency_id in old_agency_ids:
            link = LinkURLAgency(
                url_id=url_id,
                agency_id=agency_id,
            )
            links.append(link)
    await adb_client_test.add_all(links)

    # Set up pdap client to return same URLs with different information
    # - different name
    # - different description
    # - different status
    # - different approval status (approved vs. not relevant)
    # - different record type
    # - different agencies assigned
    set_up_mock_pdap_client_responses(
        mock_pdap_client=operator.pdap_client,
        responses=[
            set_up_sync_response_info(
                ids=[0, 1],
                record_type=RecordType.ACCIDENT_REPORTS,
                agency_ids=new_agency_ids,
                approval_status=ApprovalStatus.REJECTED,
                ds_url_status=DataSourcesURLStatus.BROKEN,
            ),
        ]
    )

    # Run operator
    run_info: TaskOperatorRunInfo = await operator.run_task()

    # Confirm operator ran without error
    assert_task_ran_without_error(run_info)


    # Confirm URL name, description, record type, and status are overwritten
    urls: list[URL] = await adb_client_test.get_all(URL)
    assert len(urls) == 2
    assert all([url.status == URLStatus.NOT_FOUND for url in urls])
    assert all([url.record_type == RecordType.ACCIDENT_REPORTS for url in urls])
    url_ids: list[int] = [url.id for url in urls]

    # Confirm agencies are overwritten
    links: list[LinkURLAgency] = await adb_client_test.get_all(LinkURLAgency)
    assert len(links) == 4
    assert set(link.url_id for link in links) == set(url_ids)
    assert set(link.agency_id for link in links) == set(new_agency_ids)

    # Confirm validated types overwritten
    flags: list[FlagURLValidated] = await adb_client_test.get_all(FlagURLValidated)
    assert len(flags) == 2
    assert all([flag.type == URLType.NOT_RELEVANT for flag in flags])
    assert set(flag.url_id for flag in flags) == set(url_ids)

