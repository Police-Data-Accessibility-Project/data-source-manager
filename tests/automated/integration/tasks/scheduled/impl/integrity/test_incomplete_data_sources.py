import pytest

from src.core.enums import RecordType
from src.core.tasks.scheduled.impl.integrity.operator import IntegrityMonitorTaskOperator
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from tests.automated.integration.tasks.scheduled.impl.integrity.helpers import run_task_and_confirm_error


@pytest.mark.asyncio
async def test_core(
    operator: IntegrityMonitorTaskOperator,
    test_url_id: int,
    test_agency_id: int
):
    # Check does not meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add URL as data source but without record type or validated flag
    ## App Link
    ds_app_link = DSAppLinkDataSource(
        url_id=test_url_id,
        ds_data_source_id=1
    )
    await operator.adb_client.add(ds_app_link)

    # Check meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Add validated URL flag
    flag = FlagURLValidated(
        url_id=test_url_id,
        type=URLType.DATA_SOURCE
    )
    await operator.adb_client.add(flag)
    # Check still meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Run task and confirm produces error
    await run_task_and_confirm_error(
        operator=operator,
        expected_view="integrity__incomplete_data_sources_view"
    )

    # Add record type to data source
    record_type = URLRecordType(
        url_id=test_url_id,
        record_type=RecordType.INCARCERATION_RECORDS
    )
    await operator.adb_client.add(record_type)

    # Check still meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Add agency to data source
    agency = LinkURLAgency(
        agency_id=test_agency_id,
        url_id=test_url_id
    )
    await operator.adb_client.add(agency)

    # Check no longer meets task prerequisites
    assert not await operator.meets_task_prerequisites()
