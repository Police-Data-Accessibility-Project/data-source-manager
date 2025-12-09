import pytest
from sqlalchemy import update

from src.collectors.enums import URLStatus
from src.core.tasks.scheduled.impl.update_url_status.operator import UpdateURLStatusOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_update_url_status_task(
    test_url_data_source_id: int,
    test_url_meta_url_id: int,
    adb_client_test: AsyncDatabaseClient,
    db_data_creator: DBDataCreator
):

    # Create Operator
    operator = UpdateURLStatusOperator(
        adb_client=adb_client_test,
    )

    # Add web metadata to URLs
    ## Data Source URL: Add 404
    await db_data_creator.create_web_metadata(
        url_ids=[test_url_data_source_id],
        status_code=404
    )

    ## Meta URL: Add 200
    await db_data_creator.create_web_metadata(
        url_ids=[test_url_meta_url_id],
        status_code=200
    )

    # Run Task
    await operator.run_task()

    # Check URLs
    urls: list[URL] = await adb_client_test.get_all(URL)
    id_status_set_tuple: set[tuple[int, URLStatus]] = {
        (url.id, url.status)
        for url in urls
    }
    ## Data Source URL: Status should now be broken
    ## Meta URL: Status should be unchanged
    assert id_status_set_tuple == {
        (test_url_data_source_id, URLStatus.BROKEN),
        (test_url_meta_url_id, URLStatus.OK)
    }

    # Update Web Metadata for Data Source URL to be 404
    statement = update(URLWebMetadata).where(
        URLWebMetadata.url_id == test_url_data_source_id,
    ).values(
        status_code=200
    )
    await adb_client_test.execute(statement)

    # Run Task
    await operator.run_task()

    # Check URLs
    urls: list[URL] = await adb_client_test.get_all(URL)
    id_status_set_tuple: set[tuple[int, URLStatus]] = {
        (url.id, url.status)
        for url in urls
    }
    ## Data Source URL: Status should now be ok
    ## Meta URL: Status should be unchanged
    assert id_status_set_tuple == {
        (test_url_data_source_id, URLStatus.OK),
        (test_url_meta_url_id, URLStatus.OK)
    }

