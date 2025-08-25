import pytest

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.huggingface.operator import PushToHuggingFaceTaskOperator
from src.core.tasks.scheduled.impl.huggingface.queries.get.enums import RecordTypeCoarse
from src.core.tasks.scheduled.impl.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput
from src.db.client.async_ import AsyncDatabaseClient
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.check import check_results_called
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.data import generate_expected_outputs
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.helper import setup_urls
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.models.input import \
    TestPushToHuggingFaceURLSetupEntryInput
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.enums import \
    PushToHuggingFaceTestSetupStatusEnum
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error


@pytest.mark.asyncio
async def test_huggingface_task_not_relevant_picked_up(
    adb_client_test: AsyncDatabaseClient,
    operator: PushToHuggingFaceTaskOperator
):
    record_type = RecordType.COMPLAINTS_AND_MISCONDUCT
    rt_coarse = RecordTypeCoarse.INFO_ABOUT_OFFICERS

    # Add URLs with not relevant status
    inp = TestPushToHuggingFaceURLSetupEntryInput(
        record_type=record_type,
        status=PushToHuggingFaceTestSetupStatusEnum.NOT_RELEVANT,
        has_html_content=True
    )
    url_ids: list[int] = await setup_urls(adb_client_test, inp=inp)

    # Confirm task meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Run task
    run_info: TaskOperatorRunInfo = await operator.run_task()

    # Confirm task ran without error
    assert_task_ran_without_error(run_info)

    # Confirm task no longer meets prerequisites
    assert not await operator.meets_task_prerequisites()

    # Confirm expected URLs picked up
    expected_outputs: list[GetForLoadingToHuggingFaceOutput] = generate_expected_outputs(
        url_ids=url_ids,
        relevant=False,
        record_type_fine=record_type,
        record_type_coarse=rt_coarse,
    )
    check_results_called(
        operator=operator,
        expected_outputs=expected_outputs,
    )
