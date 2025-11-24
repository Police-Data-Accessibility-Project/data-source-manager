import pytest
from sqlalchemy import delete

from src.core.tasks.scheduled.impl.integrity.operator import IntegrityMonitorTaskOperator
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from tests.automated.integration.tasks.scheduled.impl.integrity.helpers import run_task_and_confirm_error


@pytest.mark.asyncio
async def test_core(
    operator: IntegrityMonitorTaskOperator
):
    pass

    # Check does not meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add URL as data source

    # Check does not meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add same URL as Meta URL

    # Check meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Run task and confirm produces error
    await run_task_and_confirm_error(
        operator=operator,
        expected_error=""
    )

    # Delete data source link
    statement = (
        delete(
            DSAppLinkDataSource
        ).where(
            DSAppLinkDataSource.url_id == url_id
        )
    )
    await operator.adb_client.execute(statement)

    # Check no longer meets task prerequisites
    assert not await operator.meets_task_prerequisites()
