import pytest

from src.core.enums import RecordType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.sync.agency.operator import SyncAgenciesTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.flag.url_validated.enums import URLValidatedType
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
async def test_same_meta_url_diff_agency(
    wiped_database,
    operator: SyncAgenciesTaskOperator,
    db_data_creator: DBDataCreator
):
    """
    Test that, in the case of a Meta URL already linked with one agency in the DB and
    a new sync response with the same Meta URL but linked to a different agency,
    the link to the original agency should be untouched while the link to the new agency
    should be added.
    """
    db_client: AsyncDatabaseClient = operator.adb_client
    existing_agency_id: int = 1

    await db_data_creator.create_agency(existing_agency_id)
    meta_url_mapping: URLMapping = (await db_data_creator.create_validated_urls(
        validation_type=URLValidatedType.META_URL,
        record_type=RecordType.CONTACT_INFO_AND_AGENCY_META
    ))[0]
    meta_url_id: int = meta_url_mapping.url_id
    await db_data_creator.create_url_agency_links(
        url_ids=[meta_url_id],
        agency_ids=[existing_agency_id]
    )

    new_agency_id: int = 2
    meta_url: str = meta_url_mapping.url
    sync_response: AgenciesSyncResponseInfo = set_up_sync_response_info(
        agency_id=new_agency_id,
        meta_urls=[meta_url]
    )

    set_up_mock_pdap_client_responses(operator.pdap_client, [sync_response])
    run_info: TaskOperatorRunInfo = await operator.run_task()
    assert_task_run_success(run_info)

    await check_sync_concluded(db_client)

    # Confirm two agencies in the database
    agencies: list[Agency] = await db_client.get_all(Agency)
    assert len(agencies) == 2

    # Confirm 1 URL in database
    urls: list[URL] = await db_client.get_all(URL)
    assert len(urls) == 1
    assert all(url.record_type == RecordType.CONTACT_INFO_AND_AGENCY_META for url in urls)

    # Confirm 2 Agency-URL Links
    links: list[LinkURLAgency] = await db_client.get_all(LinkURLAgency)
    assert len(links) == 2

    # Confirm 2 Validated Flag
    flags: list[FlagURLValidated] = await db_client.get_all(FlagURLValidated)
    assert len(flags) == 1
    assert all(flag.type == URLValidatedType.META_URL for flag in flags)
    assert all(flag.url_id == meta_url_id for flag in flags)
