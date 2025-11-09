import pytest

from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.url.operators.submit_approved.core import SubmitApprovedURLTaskOperator
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from src.external.pdap.client import PDAPClient
from tests.helpers.asserts import assert_task_run_success


@pytest.mark.asyncio
async def test_validated_meta_url_not_included(
    db_data_creator,
    mock_pdap_client: PDAPClient,
):
    """
    If a validated Meta URL is included in the database
    This should not be included in the submit approved task
    """

    # Get Task Operator
    operator = SubmitApprovedURLTaskOperator(
        adb_client=db_data_creator.adb_client,
        pdap_client=mock_pdap_client
    )

    dbdc = db_data_creator
    url_1: int = (await dbdc.create_validated_urls(
        validation_type=URLType.META_URL
    ))[0].url_id

    # Test task operator does not meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    run_info: TaskOperatorRunInfo = await operator.run_task()
    assert_task_run_success(run_info)

    # Confirm entry not included in database
    ds_urls: list[DSAppLinkDataSource] = await dbdc.adb_client.get_all(DSAppLinkDataSource)
    assert len(ds_urls) == 0
