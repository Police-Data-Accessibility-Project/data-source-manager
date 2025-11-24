from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.integrity.operator import IntegrityMonitorTaskOperator
from src.core.tasks.url.enums import TaskOperatorOutcome


async def run_task_and_confirm_error(
    operator: IntegrityMonitorTaskOperator,
    expected_error: str
) -> None:
    run_info: TaskOperatorRunInfo = await operator.run_task()
    assert run_info.outcome == TaskOperatorOutcome.ERROR
    assert run_info.error_message == expected_error