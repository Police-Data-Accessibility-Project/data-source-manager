import pytest

from src.core.enums import RecordType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.huggingface.operator import PushToHuggingFaceTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.check import check_not_called
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.enums import \
    PushToHuggingFaceTestSetupStatusEnum
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.helper import setup_urls
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.models.input import \
    TestPushToHuggingFaceURLSetupEntryInput
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error


@pytest.mark.asyncio
async def test_huggingface_task_not_validated_not_picked_up(
    adb_client_test: AsyncDatabaseClient,
    operator: PushToHuggingFaceTaskOperator
):
    record_type = RecordType.COURT_CASES

    # Add URLs with pending status
    inp = TestPushToHuggingFaceURLSetupEntryInput(
        record_type=record_type,
        status=PushToHuggingFaceTestSetupStatusEnum.NOT_VALIDATED,
        has_html_content=True
    )
    _ = await setup_urls(adb_client_test, inp=inp)

    # Confirm task doesn't meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Run task as though it did meet prerequisites
    run_info: TaskOperatorRunInfo = await operator.run_task()

    # Confirm task ran without error
    assert_task_ran_without_error(run_info)

    # Confirm task still doesn't meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Confirm pending URL not picked up
    check_not_called(operator)
