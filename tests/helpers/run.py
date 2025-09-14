from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from tests.helpers.asserts import assert_task_run_success


async def run_task_and_confirm_success(
    operator: URLTaskOperatorBase,
) -> None:
    """
    Run task, confirm success, and assert task no longer meets prerequisites.
    """

    run_info: TaskOperatorRunInfo = await operator.run_task()
    assert_task_run_success(run_info)
    assert not await operator.meets_task_prerequisites()