import pytest

from src.core.enums import RecordType
from src.core.tasks.scheduled.impl.integrity.operator import IntegrityMonitorTaskOperator
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from tests.automated.integration.tasks.scheduled.impl.integrity.helpers import run_task_and_confirm_error


@pytest.mark.asyncio
async def test_core(
    operator: IntegrityMonitorTaskOperator
):
    pass

    # Check does not meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add URL as data source but without record type or validated flag
    ## URL
    url = URL(
        url="example.com",
        source=URLSource.COLLECTOR,
        trailing_slash=False
    )
    url_id: int = await operator.adb_client.add(url, return_id=True)

    ## App Link
    ds_app_link = DSAppLinkDataSource(
        url_id=url_id,
        ds_data_source_id=1
    )
    await operator.adb_client.add(ds_app_link)

    # Check meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Add validated URL flag
    flag = FlagURLValidated(
        url_id=url_id,
        type=URLType.DATA_SOURCE
    )
    await operator.adb_client.add(flag)
    # Check still meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Run task and confirm produces error
    await run_task_and_confirm_error(
        operator=operator,
        expected_error=""
    )

    # Add record type to data source
    record_type = URLRecordType(
        url_id=url_id,
        record_type=RecordType.INCARCERATION_RECORDS
    )

    # Check no longer meets task prerequisites
    assert not await operator.meets_task_prerequisites()
