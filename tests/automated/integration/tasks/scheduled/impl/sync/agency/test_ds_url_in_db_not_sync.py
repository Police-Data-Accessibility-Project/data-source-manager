import pytest

from src.core.enums import RecordType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.sync.agency.operator import SyncAgenciesTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInfo
from tests.automated.integration.tasks.scheduled.impl.sync.agency.helpers import check_sync_concluded
from tests.automated.integration.tasks.scheduled.impl.sync.agency.setup.core import set_up_sync_response_info, \
    set_up_mock_pdap_client_responses
from tests.helpers.asserts import assert_task_run_success
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_data_sources_url_in_db_not_meta_url_sync(
    wiped_database,
    operator: SyncAgenciesTaskOperator,
    db_data_creator: DBDataCreator
):
    """
    In an Agency Sync, a URL validated as a Data Source linked to the agency
    should be untouched if the URL is not in the sync response.
    """
    db_client: AsyncDatabaseClient = operator.adb_client

    agency_id: int = 1

    # Create agency
    await db_data_creator.create_agency(agency_id)

    # Set up sync response with new meta URL
    sync_response: AgenciesSyncResponseInfo = set_up_sync_response_info(
        agency_id=agency_id,
        meta_urls=[
            "https://example.com/meta-url-1",
        ]
    )

    # Create additional URL Validated as data source and link to agency
    ds_url_mapping: URLMapping = (await db_data_creator.create_validated_urls(
        validation_type=URLType.DATA_SOURCE,
        record_type=RecordType.ACCIDENT_REPORTS
    ))[0]
    ds_url_id: int = ds_url_mapping.url_id
    await db_data_creator.create_url_agency_links(
        url_ids=[ds_url_id],
        agency_ids=[agency_id]
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
    assert set(url.record_type for url in urls) == {
        RecordType.CONTACT_INFO_AND_AGENCY_META,
        RecordType.ACCIDENT_REPORTS
    }

    # Confirm 2 Agency-URL Links
    links: list[LinkURLAgency] = await db_client.get_all(LinkURLAgency)
    assert len(links) == 2
    assert all(link.agency_id == 1 for link in links)
    assert set(link.url_id for link in links) == set(url.id for url in urls)

    # Confirm 2 Validated Flags with different Validation Types
    flags: list[FlagURLValidated] = await db_client.get_all(FlagURLValidated)
    assert len(flags) == 2
    assert set(flag.type for flag in flags) == {
        URLType.META_URL,
        URLType.DATA_SOURCE
    }
    assert set(flag.url_id for flag in flags) == set(url.id for url in urls)

