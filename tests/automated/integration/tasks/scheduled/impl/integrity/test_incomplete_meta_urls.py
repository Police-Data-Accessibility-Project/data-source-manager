import pytest

from src.core.tasks.scheduled.impl.integrity.operator import IntegrityMonitorTaskOperator
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from tests.automated.integration.tasks.scheduled.impl.integrity.helpers import run_task_and_confirm_error


@pytest.mark.asyncio
async def test_core(
    operator: IntegrityMonitorTaskOperator,
    test_agency_id: int,
    test_url_id: int
):
    # Check does not meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add Meta URL without linking an agency to it
    ## Validated Flag
    flag = FlagURLValidated(
        url_id=test_url_id,
        type=URLType.META_URL
    )
    await operator.adb_client.add(flag)

    ## App Link
    ds_app_link = DSAppLinkMetaURL(
        url_id=test_url_id,
        ds_meta_url_id=1
    )
    await operator.adb_client.add(ds_app_link)

    # Check meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Run task and confirm produces error
    await run_task_and_confirm_error(
        operator=operator,
        expected_view="integrity__incomplete_meta_urls_view"
    )

    # Add agency to Meta URL
    link = LinkURLAgency(
        agency_id=test_agency_id,
        url_id=test_url_id
    )
    await operator.adb_client.add(link)

    # Check no longer meets task prerequisites
    assert not await operator.meets_task_prerequisites()


