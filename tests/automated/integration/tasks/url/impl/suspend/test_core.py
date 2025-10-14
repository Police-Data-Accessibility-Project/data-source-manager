import pytest

from src.core.tasks.url.operators.suspend.core import SuspendURLTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_suspended.sqlalchemy import FlagURLSuspended
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_suspend_task(
    adb_client_test: AsyncDatabaseClient,
    db_data_creator: DBDataCreator,
):
    operator = SuspendURLTaskOperator(
        adb_client=adb_client_test
    )

    assert not await operator.meets_task_prerequisites()

    url_id_1: int = (await db_data_creator.create_urls(count=1))[0].url_id

    assert not await operator.meets_task_prerequisites()

    await db_data_creator.not_found_location_suggestion(url_id=url_id_1)

    assert not await operator.meets_task_prerequisites()

    await db_data_creator.not_found_location_suggestion(url_id=url_id_1)

    assert await operator.meets_task_prerequisites()

    await run_task_and_confirm_success(operator)

    url_id_2: int = (await db_data_creator.create_urls(count=1))[0].url_id

    await db_data_creator.not_found_agency_suggestion(url_id=url_id_2)

    assert not await operator.meets_task_prerequisites()

    await db_data_creator.not_found_agency_suggestion(url_id=url_id_2)

    assert await operator.meets_task_prerequisites()

    await run_task_and_confirm_success(operator)

    flags: list[FlagURLSuspended] = await adb_client_test.get_all(FlagURLSuspended)
    assert len(flags) == 2

    assert {flag.url_id for flag in flags} == {url_id_1, url_id_2}