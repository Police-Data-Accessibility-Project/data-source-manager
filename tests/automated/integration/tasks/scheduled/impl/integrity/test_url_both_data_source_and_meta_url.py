import pytest
from sqlalchemy import delete

from src.core.tasks.scheduled.impl.integrity.operator import IntegrityMonitorTaskOperator
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from tests.automated.integration.tasks.scheduled.impl.integrity.helpers import run_task_and_confirm_error


@pytest.mark.asyncio
async def test_core(
    operator: IntegrityMonitorTaskOperator,
    test_url_data_source_id: int
):

    # Check does not meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add DS App Link
    ds_app_link_ds = DSAppLinkDataSource(
        url_id=test_url_data_source_id,
        ds_data_source_id=1
    )
    await operator.adb_client.add(ds_app_link_ds)

    # Add same URL as Meta URL
    ## App Link
    ds_app_link_mu = DSAppLinkMetaURL(
        url_id=test_url_data_source_id,
        ds_meta_url_id=1
    )
    await operator.adb_client.add(ds_app_link_mu)

    # Check meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Run task and confirm produces error
    await run_task_and_confirm_error(
        operator=operator,
        expected_view="integrity__url_both_data_source_and_meta_url_view"
    )

    # Delete data source link
    statement = (
        delete(
            DSAppLinkMetaURL
        ).where(
            DSAppLinkMetaURL.url_id == test_url_data_source_id
        )
    )
    await operator.adb_client.execute(statement)

    # Check no longer meets task prerequisites
    assert not await operator.meets_task_prerequisites()
