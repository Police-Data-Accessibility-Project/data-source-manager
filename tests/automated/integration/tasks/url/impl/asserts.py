from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.mixins.prereq import HasPrerequisitesMixin
from src.core.tasks.url.enums import TaskOperatorOutcome


async def assert_prereqs_not_met(operator: HasPrerequisitesMixin) -> None:
    meets_prereqs = await operator.meets_task_prerequisites()
    assert not meets_prereqs

async def assert_prereqs_met(operator: HasPrerequisitesMixin) -> None:
    meets_prereqs = await operator.meets_task_prerequisites()
    assert meets_prereqs

def assert_task_ran_without_error(run_info: TaskOperatorRunInfo) -> None:
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS, run_info.message

