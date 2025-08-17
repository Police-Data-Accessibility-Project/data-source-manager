from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.db.enums import TaskType
from tests.automated.integration.core.async_.conclude_task.setup_info import TestAsyncCoreSetupInfo


def setup_run_info(
    setup_info: TestAsyncCoreSetupInfo,
    outcome: TaskOperatorOutcome,
    message: str = ""
):
    run_info = TaskOperatorRunInfo(
        task_id=setup_info.task_id,
        task_type=TaskType.HTML,
        outcome=outcome,
        message=message,
    )
    return run_info