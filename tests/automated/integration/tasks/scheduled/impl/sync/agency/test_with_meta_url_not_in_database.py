import pytest

from src.core.enums import RecordType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.sync.agency.operator import SyncAgenciesTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo, AgenciesSyncResponseInfo
from tests.automated.integration.tasks.scheduled.impl.sync.agency.helpers import patch_sync_agencies, \
    check_sync_concluded
from tests.automated.integration.tasks.scheduled.impl.sync.agency.setup.core import set_up_sync_response_info, \
    set_up_mock_pdap_client_responses
from tests.helpers.asserts import assert_task_run_success


@pytest.mark.asyncio
async def test_with_meta_url_not_in_database(
    wiped_database,
    operator: SyncAgenciesTaskOperator
):
    """
    In an Agency Sync, a Meta URL included in the sync response
    but not present in the DB should be added to the DB with:
    - The URLValidationFlag set to `Meta URL`
    - The Record Type set to `Contact Info and Agency Meta`
    - The link to the agency added
    """
    db_client: AsyncDatabaseClient = operator.adb_client

    sync_response: AgenciesSyncResponseInfo = set_up_sync_response_info(
        agency_id=1,
        meta_urls=[
            "https://example.com/meta-url-1",
            "https://example.com/meta-url-2",
        ]
    )

    set_up_mock_pdap_client_responses(operator.pdap_client, [sync_response])
    run_info: TaskOperatorRunInfo = await operator.run_task()
    assert_task_run_success(run_info)

    await check_sync_concluded(db_client)

    # Confirm one agency in the database
    agencies: list[Agency] = await db_client.get_all(Agency)
    assert len(agencies) == 1

    # Confirm 2 URLs in database
    urls: list[URL] = await db_client.get_all(URL)
    assert len(urls) == 2
    assert all(url.record_type == RecordType.CONTACT_INFO_AND_AGENCY_META for url in urls)

    # Confirm 2 Agency-URL Links
    links: list[LinkURLAgency] = await db_client.get_all(LinkURLAgency)
    assert len(links) == 2
    assert all(link.agency_id == 1 for link in links)
    assert set(link.url_id for link in links) == set(url.id for url in urls)

    # Confirm 2 Validated Flags
    flags: list[FlagURLValidated] = await db_client.get_all(FlagURLValidated)
    assert len(flags) == 2
    assert all(flag.type == URLType.META_URL for flag in flags)
    assert set(flag.url_id for flag in flags) == set(url.id for url in urls)
